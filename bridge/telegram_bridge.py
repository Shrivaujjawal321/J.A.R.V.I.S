"""
Telegram Bridge for Jarvis.

Listens to the Telegram bot and forwards messages to the jarvis-core daemon
(HTTP) or the `claude` CLI (subprocess fallback). Responses go back to Telegram.

Also hosts the **WhatsApp task-approval relay**: when the WhatsApp gateway
(whatsapp/gateway.mjs) detects that someone asked Jarvis to DO a real-world
task, it appends a request to whatsapp/state/task_approvals.jsonl. This bridge
tails that file, pings Boss on Telegram, and — when Boss replies to that ping —
writes the answer to whatsapp/state/whatsapp_outbox.jsonl, which the gateway
sends back to the original person as Jarvis.

Run as a background service (systemd). Setup:
1. Bot via @BotFather → TELEGRAM_BOT_TOKEN in .env
2. ALLOWED_USER_IDS=<your telegram id>   (REQUIRED — bridge refuses to start open)
3. pip install -r requirements.txt
4. python telegram_bridge.py
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationHandlerStop,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Voice message support (parallel branch — does not affect text handling)
try:
    from voice_handler import handle_voice_message as _handle_voice_message
    VOICE_ENABLED = True
except ImportError:
    VOICE_ENABLED = False

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("jarvis.bridge")

# === Configuration ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
JARVIS_PROJECT_PATH = os.getenv("JARVIS_PROJECT_PATH", str(Path(__file__).parent.parent))
ALLOWED_USER_IDS = [int(x) for x in os.getenv("ALLOWED_USER_IDS", "").split(",") if x]
CLAUDE_TIMEOUT = int(os.getenv("CLAUDE_TIMEOUT", "180"))  # seconds
MAX_TURNS = int(os.getenv("MAX_TURNS", "15"))

# jarvis-core daemon (Phase 1: text via super-agent orchestrator)
JARVIS_CORE_URL = os.getenv("JARVIS_CORE_URL", "http://127.0.0.1:8765")
USE_DAEMON = os.getenv("JARVIS_USE_DAEMON", "1") != "0"

BOSS_CHAT_ID = ALLOWED_USER_IDS[0] if ALLOWED_USER_IDS else None

# WhatsApp relay paths
WA_STATE = Path(JARVIS_PROJECT_PATH) / "whatsapp" / "state"
WA_APPROVALS = WA_STATE / "task_approvals.jsonl"
WA_OUTBOX = WA_STATE / "whatsapp_outbox.jsonl"
WA_OFFSET = WA_STATE / ".tg_approvals_offset"
WA_PENDING_FILE = WA_STATE / "tg_pending.json"

# LinkedIn modules — single top-level guarded import (no per-call sys.path growth)
if JARVIS_PROJECT_PATH not in sys.path:
    sys.path.insert(0, JARVIS_PROJECT_PATH)
try:
    from scripts.linkedin import telegram_approval as la  # type: ignore
except Exception as _e:  # pragma: no cover
    la = None
    log.warning("LinkedIn telegram_approval import failed: %s", _e)
try:
    from scripts.linkedin import reporter as lp_reporter  # type: ignore
except Exception as _e:  # pragma: no cover
    lp_reporter = None
    log.warning("LinkedIn reporter import failed: %s", _e)


def is_authorized(user_id: int) -> bool:
    """Fail CLOSED: if ALLOWED_USER_IDS is unset, deny everyone (no open relay)."""
    if not ALLOWED_USER_IDS:
        return False
    return user_id in ALLOWED_USER_IDS


# === Safe sending (Markdown crash-proof + entity-safe chunking) ===============

def smart_chunks(text: str, size: int = 3800):
    """Split text under Telegram's 4096 limit, breaking at newlines (never mid-line
    unless a single line exceeds `size`). Keeps code blocks/entities far more intact
    than a naive byte slice."""
    text = text or ""
    if len(text) <= size:
        yield text
        return
    buf = ""
    for line in text.split("\n"):
        if len(line) > size:
            if buf:
                yield buf
                buf = ""
            for i in range(0, len(line), size):
                yield line[i : i + size]
            continue
        if len(buf) + len(line) + 1 > size:
            yield buf
            buf = line
        else:
            buf = (buf + "\n" + line) if buf else line
    if buf:
        yield buf


async def reply(message, text: str, markdown: bool = True):
    """Reply, chunked + crash-proof: try Markdown, fall back to plain text on any
    parse error so a stray * / _ / ` never silently drops the message."""
    for chunk in smart_chunks(text):
        if not chunk:
            continue
        try:
            await message.reply_text(chunk, parse_mode="Markdown" if markdown else None)
        except Exception:
            try:
                await message.reply_text(chunk)  # plain fallback
            except Exception as e:
                log.error("reply failed even plain: %s", e)


async def send_to(bot, chat_id, text: str, markdown: bool = True):
    """Proactive send (chunked + Markdown-safe)."""
    for chunk in smart_chunks(text):
        if not chunk:
            continue
        try:
            await bot.send_message(chat_id, chunk, parse_mode="Markdown" if markdown else None)
        except Exception:
            try:
                await bot.send_message(chat_id, chunk)
            except Exception as e:
                log.error("send_to failed even plain: %s", e)


async def run_cli(args: list[str], timeout: int = 60) -> tuple[int, str]:
    """Async subprocess runner — NEVER blocks the event loop (unlike subprocess.run)."""
    try:
        proc = await asyncio.create_subprocess_exec(
            ".venv/bin/python", *args,
            cwd=JARVIS_PROJECT_PATH,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return proc.returncode, (out.decode(errors="replace") + err.decode(errors="replace"))
    except asyncio.TimeoutError:
        return 124, f"Timeout after {timeout}s"
    except Exception as e:
        return 1, f"Subprocess error: {e}"


# === Claude / daemon dispatch =================================================

async def _call_via_subprocess(prompt: str) -> str:
    """Legacy fallback: spawn `claude` CLI directly. Used when daemon is down."""
    cmd = ["claude", "-p", prompt, "--output-format", "json", "--max-turns", str(MAX_TURNS)]
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd, cwd=JARVIS_PROJECT_PATH,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=CLAUDE_TIMEOUT)
        if process.returncode != 0:
            return f"⚠️ Jarvis error: {stderr.decode()[:500]}"
        try:
            data = json.loads(stdout.decode())
            if isinstance(data, dict):
                return data.get("result") or data.get("response") or str(data)[:2000]
            return str(data)[:2000]
        except json.JSONDecodeError:
            return stdout.decode()[:2000]
    except asyncio.TimeoutError:
        return "⏱️ Jarvis took too long. Try a simpler request."
    except Exception as e:
        return f"❌ Error reaching Jarvis (fallback): {e}"


async def _call_via_daemon(prompt: str, user_id: int) -> str:
    """Phase 1 path: send to jarvis-core daemon over HTTP. Short connect timeout so a
    down daemon fails over to subprocess fast (not after the full read timeout)."""
    timeout = httpx.Timeout(connect=5.0, read=CLAUDE_TIMEOUT, write=10.0, pool=5.0)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{JARVIS_CORE_URL}/chat",
                json={
                    "user_id": str(user_id),
                    "message": prompt,
                    "resume_session": True,
                    "max_turns": MAX_TURNS,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("reply") or "(empty reply from jarvis-core)"
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout) as e:
        log.warning("jarvis-core unreachable (%s), falling back to subprocess", type(e).__name__)
        return await _call_via_subprocess(prompt)
    except Exception as e:
        return f"❌ jarvis-core error: {type(e).__name__}: {e}"


async def call_claude(prompt: str, user_id: int = 0) -> str:
    if USE_DAEMON:
        return await _call_via_daemon(prompt, user_id=user_id)
    return await _call_via_subprocess(prompt)


# === Telegram Handlers ========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("Sorry, this bot is private.")
        return
    await reply(
        update.message,
        "👋 *Jarvis here.* Type anything — I'll handle it.\n\n"
        "Try:\n"
        "• What's my schedule today?\n"
        "• Triage my inbox\n"
        "• /briefing\n"
        "• Add task: call mom tomorrow\n\n"
        "Full command list: /help",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    await reply(
        update.message,
        "📋 *Jarvis commands*\n\n"
        "*Daily*\n"
        "/briefing · /triage · /plan_day · /weekly_review · /digest_now\n\n"
        "*WhatsApp relay*\n"
        "/wa_pending — pending task approvals\n"
        "/wa_reply <id> <text> — answer a pending request as Jarvis\n"
        "/wa_ignore <id> — drop a pending request\n"
        "_(or just Reply to a 📲 WhatsApp ping to answer as Jarvis)_\n\n"
        "*Autonomous goals*\n"
        "/goal_add <desc> · /goals · /goal_status <id> · /goal_approve <id> · /goal_reject <id>\n\n"
        "*Self-growth*\n"
        "/growth_list · /growth_approve <id> · /growth_reject <id>\n\n"
        "*Hackathon War Room*\n"
        "/wr_start <slug> · /wr_status [slug] · /wr_run <slug> · /wr_checkpoint <slug> <decision> · /wr_pick <slug> <ids>\n\n"
        "*LinkedIn*\n"
        "/lp_status · /lp_approve_all · /lp_approve <ids> · /lp_reject <ids> · /lp_run · /lp_report\n\n"
        "Or just type naturally — I'll route it.",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    if not update.message or not update.message.text:
        return
    user_message = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    response = await call_claude(user_message, user_id=update.effective_user.id)
    await reply(update.message, response)


# Telegram disallows hyphens in command names — map underscored aliases
# back to Claude's hyphenated slash commands.
SLASH_ALIASES = {
    "briefing": "/briefing",
    "triage": "/triage",
    "plan_day": "/plan-day",
    "weekly_review": "/weekly-review",
}


async def handle_slash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forward bot commands to Claude as slash commands."""
    if not is_authorized(update.effective_user.id):
        return
    if not update.message or not update.message.text:
        return
    raw = update.message.text.lstrip("/").split("@", 1)[0].split()[0]
    cmd = SLASH_ALIASES.get(raw, f"/{raw}")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    response = await call_claude(cmd, user_id=update.effective_user.id)
    await reply(update.message, response)


# === WhatsApp task-approval relay =============================================
# In-memory pending map (persisted to WA_PENDING_FILE so a bridge restart keeps
# the reply→chat routing). id -> {jid, name, request, tg_msg_id}
wa_pending: dict[str, dict] = {}
wa_msg_index: dict[int, str] = {}  # telegram reply-target msg_id -> request id


def _save_pending():
    try:
        WA_STATE.mkdir(parents=True, exist_ok=True)
        WA_PENDING_FILE.write_text(json.dumps(wa_pending))
    except Exception as e:
        log.error("save pending failed: %s", e)


def _load_pending():
    global wa_pending, wa_msg_index
    try:
        if WA_PENDING_FILE.exists():
            wa_pending = json.loads(WA_PENDING_FILE.read_text())
            wa_msg_index = {v["tg_msg_id"]: k for k, v in wa_pending.items() if v.get("tg_msg_id")}
    except Exception as e:
        log.error("load pending failed: %s", e)
        wa_pending, wa_msg_index = {}, {}


async def _poll_wa_approvals(app):
    """Tail task_approvals.jsonl by byte offset; ping Boss for each new task.
    Offset is initialized once in wa_relay_loop, so here it always exists (default 0)
    and a freshly-created file's first task is NOT mistaken for history."""
    if not WA_APPROVALS.exists() or BOSS_CHAT_ID is None:
        return
    try:
        off = int(WA_OFFSET.read_text()) if WA_OFFSET.exists() else 0
    except Exception:
        off = 0
    size = WA_APPROVALS.stat().st_size
    if size <= off:
        if size < off:  # file was truncated/rotated
            WA_OFFSET.write_text(str(size))
        return
    with open(WA_APPROVALS, "rb") as f:
        f.seek(off)
        data = f.read()
    WA_OFFSET.write_text(str(off + len(data)))  # advance first (no double-ping on crash)
    for line in data.decode("utf-8", "replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue
        rid = req.get("id")
        jid = req.get("jid")
        if not rid or not jid:
            continue
        name = req.get("name", "someone")
        request = req.get("request", "")
        text = (
            f"📲 *WhatsApp* — *{name}* wants something done:\n\n"
            f"“{request}”\n\n"
            f"👉 *To answer as Jarvis*, either:\n"
            f"   • *Swipe/long-press this message → Reply* → type your answer, OR\n"
            f"   • send `/wa_reply {rid} <your answer>`\n"
            f"To drop it: `/wa_ignore {rid}`"
        )
        try:
            msg = await app.bot.send_message(BOSS_CHAT_ID, text, parse_mode="Markdown")
        except Exception:
            msg = await app.bot.send_message(BOSS_CHAT_ID, text)  # plain fallback
        wa_pending[rid] = {"jid": jid, "name": name, "request": request, "tg_msg_id": msg.message_id}
        wa_msg_index[msg.message_id] = rid
        _save_pending()
        log.info("WA task ping sent to Boss: id=%s from=%s", rid, name)


async def wa_relay_loop(app):
    """Background poller started in post_init."""
    # Initialize offset ONCE at startup: skip whatever history already exists, but
    # do it now (not lazily) so the first task that *creates* the file is caught.
    if not WA_OFFSET.exists():
        WA_STATE.mkdir(parents=True, exist_ok=True)
        start_size = WA_APPROVALS.stat().st_size if WA_APPROVALS.exists() else 0
        WA_OFFSET.write_text(str(start_size))
    log.info("WhatsApp relay loop started (watching %s, offset=%s)",
             WA_APPROVALS, WA_OFFSET.read_text() if WA_OFFSET.exists() else "0")
    while True:
        try:
            await _poll_wa_approvals(app)
        except Exception as e:
            log.error("wa relay loop error: %s", e)
        await asyncio.sleep(3)


async def wa_reply_capture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """If Boss REPLIES to a 📲 WhatsApp ping, relay his text to that person as Jarvis.
    Runs in group -1 (before handle_message). If it's not a WA reply, returns so the
    normal text handler still fires."""
    if not is_authorized(update.effective_user.id):
        return
    m = update.message
    if not m or not m.reply_to_message or not m.text:
        return
    rid = wa_msg_index.get(m.reply_to_message.message_id)
    if not rid:
        return  # not a WA reply — let handle_message run
    ok, info = _deliver_wa_reply(rid, m.text)
    if ok:
        await m.reply_text(f"✅ Sent to *{info}* as Jarvis.", parse_mode="Markdown")
    else:
        await m.reply_text(f"⚠️ {info}")
    raise ApplicationHandlerStop


def _deliver_wa_reply(rid: str, text: str) -> tuple[bool, str]:
    """Queue Boss's answer to the WhatsApp outbox + clear the pending entry."""
    info = wa_pending.get(rid)
    if not info:
        return (False, f"no pending task `{rid}` (expired or already handled)")
    try:
        WA_STATE.mkdir(parents=True, exist_ok=True)
        with open(WA_OUTBOX, "a") as f:
            f.write(json.dumps({"id": rid, "jid": info["jid"], "text": text}) + "\n")
    except Exception as e:
        return (False, f"could not queue: {e}")
    wa_pending.pop(rid, None)
    wa_msg_index.pop(info.get("tg_msg_id"), None)
    _save_pending()
    return (True, info.get("name", "them"))


async def cmd_wa_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Explicit relay reply (no Telegram reply-gesture needed): /wa_reply <id> <text>."""
    if not is_authorized(update.effective_user.id):
        return
    parts = (update.message.text or "").split(maxsplit=2)
    if len(parts) < 3:
        await update.message.reply_text(
            "Usage: `/wa_reply <id> <your answer>`\nSee pending: /wa_pending", parse_mode="Markdown")
        return
    rid, answer = parts[1], parts[2]
    ok, info = _deliver_wa_reply(rid, answer)
    if ok:
        await update.message.reply_text(f"✅ Sent to *{info}* as Jarvis.", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ {info}")


async def cmd_wa_pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    if not wa_pending:
        await update.message.reply_text("📲 No WhatsApp task approvals pending.")
        return
    lines = [f"📲 *Pending WhatsApp tasks ({len(wa_pending)})*", ""]
    for rid, info in list(wa_pending.items())[:20]:
        lines.append(f"• `{rid}` — *{info.get('name','?')}*")
        lines.append(f"  _{info.get('request','')[:120]}_")
    lines.append("\nReply to the original 📲 ping to answer, or `/wa_ignore <id>`.")
    await reply(update.message, "\n".join(lines))


async def cmd_wa_ignore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    parts = (update.message.text or "").split()
    if len(parts) < 2:
        await update.message.reply_text("Usage: `/wa_ignore <id>`", parse_mode="Markdown")
        return
    rid = parts[1]
    info = wa_pending.pop(rid, None)
    if info:
        wa_msg_index.pop(info.get("tg_msg_id"), None)
        _save_pending()
        await update.message.reply_text(f"🗑️ Dropped pending task `{rid}`.", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"No pending task `{rid}`.", parse_mode="Markdown")


# === Phase 3: Autonomous goal commands ========================================

async def _post_json(path: str, payload: dict) -> dict:
    timeout = httpx.Timeout(connect=5.0, read=CLAUDE_TIMEOUT, write=10.0, pool=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.post(f"{JARVIS_CORE_URL}{path}", json=payload)
        r.raise_for_status()
        return r.json()


async def _get_json(path: str, params: dict | None = None) -> dict:
    timeout = httpx.Timeout(connect=5.0, read=CLAUDE_TIMEOUT, write=10.0, pool=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.get(f"{JARVIS_CORE_URL}{path}", params=params or {})
        r.raise_for_status()
        return r.json()


async def cmd_goal_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    description = (update.message.text or "").split(maxsplit=1)
    if len(description) < 2:
        await reply(
            update.message,
            "Usage: `/goal_add <description>`\n"
            "Example: `/goal_add research 3 papers on prompt caching, summarize each in 5 bullets`",
        )
        return
    try:
        result = await _post_json(
            "/goal",
            {"user_id": str(update.effective_user.id), "description": description[1].strip()},
        )
        await reply(
            update.message,
            f"🎯 Goal queued: `{result['goal_id']}`\n"
            f"Status: `{result['status']}`\n"
            f"Scheduler picks it up within 60s. Track: `/goal_status {result['goal_id']}`.",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Could not create goal: {e}")


async def cmd_goals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    try:
        goals = await _get_json("/goals", {"limit": 20})
    except Exception as e:
        await update.message.reply_text(f"❌ Could not list goals: {e}")
        return
    if not goals:
        await update.message.reply_text("No goals yet. Use /goal_add <description> to start.")
        return
    lines = ["📋 *Recent goals* (most recent first)"]
    for g in goals[:15]:
        emoji = {
            "queued": "🕒", "planning": "🧩", "running": "🏃", "awaiting_approval": "🔐",
            "completed": "✅", "failed": "⚠️", "cancelled": "❌",
        }.get(g["status"], "•")
        desc = (g["description"][:80] + "…") if len(g["description"]) > 80 else g["description"]
        lines.append(f"{emoji} `{g['goal_id']}` · _{g['status']}_ · {desc}")
    await reply(update.message, "\n".join(lines))


async def cmd_goal_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    parts = (update.message.text or "").split()
    if len(parts) < 2:
        await update.message.reply_text("Usage: `/goal_status <goal_id>`", parse_mode="Markdown")
        return
    goal_id = parts[1]
    try:
        out = await _get_json(f"/goal/{goal_id}/output")
    except Exception as e:
        await update.message.reply_text(f"❌ Could not fetch goal: {e}")
        return
    lines = [f"🎯 *Goal `{out['goal_id']}`* — `{out['status']}`"]
    if out.get("plan_summary"):
        lines.append(f"_{out['plan_summary']}_")
    lines.append(f"💰 ${out.get('cost_usd_total', 0):.4f}")
    lines.append("")
    for s in out.get("sub_tasks", []):
        tier_mark = ["", "🟢T1", "🟡T2", "🔴T3"][s.get("tier", 1)]
        lines.append(f"  • {tier_mark} *{s['label']}*")
        if s.get("error"):
            lines.append(f"    ⚠️ {s['error'][:200]}")
        elif s.get("output"):
            preview = s["output"][:300].replace("\n", " ")
            lines.append(f"    _{preview}…_" if len(s["output"]) > 300 else f"    _{preview}_")
        if s.get("approval_id"):
            lines.append(f"    🔐 needs approval: `{s['approval_id']}`")
    if out.get("error"):
        lines.append(f"\n⚠️ Goal error: {out['error']}")
    if out.get("final_output"):
        lines.append("\n*Final output saved* — full text via daemon /goal/{id}/output")
    await reply(update.message, "\n".join(lines)[:3900])


async def cmd_goal_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    parts = (update.message.text or "").split(maxsplit=2)
    if len(parts) < 2:
        await update.message.reply_text("Usage: `/goal_approve <approval_id> [note]`", parse_mode="Markdown")
        return
    approval_id = parts[1]
    note = parts[2] if len(parts) >= 3 else None
    try:
        result = await _post_json(
            f"/approval/{approval_id}/decide",
            {"decision": "approved", "boss_note": note, "decided_by": str(update.effective_user.id)},
        )
        await reply(update.message, f"✅ Approved `{approval_id}` — resumed={result.get('resumed', False)}")
    except Exception as e:
        await update.message.reply_text(f"❌ Could not approve: {e}")


async def cmd_goal_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    parts = (update.message.text or "").split(maxsplit=2)
    if len(parts) < 2:
        await update.message.reply_text("Usage: `/goal_reject <approval_id> [reason]`", parse_mode="Markdown")
        return
    approval_id = parts[1]
    note = parts[2] if len(parts) >= 3 else None
    try:
        result = await _post_json(
            f"/approval/{approval_id}/decide",
            {"decision": "rejected", "boss_note": note, "decided_by": str(update.effective_user.id)},
        )
        await reply(update.message, f"❌ Rejected `{approval_id}` — resumed={result.get('resumed', False)}")
    except Exception as e:
        await update.message.reply_text(f"❌ Could not reject: {e}")


async def cmd_digest_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """On-demand digest (vs the cron one at 06:30 IST). Async — no loop block."""
    if not is_authorized(update.effective_user.id):
        return
    rc, text = await run_cli(["scripts/morning_digest.py", "--stdout", "--hours", "24"], timeout=30)
    await reply(update.message, text or "(no output)")


# === Self-growth commands (Phase E) — local file-backed approval queue ========

def _growth_dir() -> Path:
    return Path(JARVIS_PROJECT_PATH) / "data" / "growth"


def _list_growth_approvals() -> list[dict]:
    pending_dir = _growth_dir() / "awaiting_approval"
    if not pending_dir.exists():
        return []
    out: list[dict] = []
    for f in sorted(pending_dir.glob("growth-*.json")):
        try:
            obj = json.loads(f.read_text())
        except Exception:
            continue
        if obj.get("status") == "pending":
            obj["_path"] = str(f)
            out.append(obj)
    return out


def _resolve_growth_approval(approval_id: str, decision: str, note: str | None) -> tuple[bool, str]:
    pending_dir = _growth_dir() / "awaiting_approval"
    decided_dir = _growth_dir() / ("approved" if decision == "approved" else "rejected")
    decided_dir.mkdir(parents=True, exist_ok=True)
    src = pending_dir / f"{approval_id}.json"
    if not src.exists():
        return (False, f"no such approval `{approval_id}`")
    try:
        obj = json.loads(src.read_text())
    except Exception as exc:
        return (False, f"corrupt approval file: {exc}")
    obj["status"] = decision
    obj["decided_at"] = datetime.utcnow().isoformat() + "Z"
    if note:
        obj["boss_note"] = note
    dest = decided_dir / src.name
    dest.write_text(json.dumps(obj, indent=2))
    src.unlink()
    return (True, f"moved to {dest.relative_to(Path(JARVIS_PROJECT_PATH))}")


async def cmd_growth_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    pending = _list_growth_approvals()
    if not pending:
        await update.message.reply_text("🌱 No growth approvals pending.")
        return
    lines = [f"🌱 *Growth approvals pending ({len(pending)})*", ""]
    for entry in pending[:20]:
        prop = entry.get("proposal", {})
        aid = entry.get("approval_id", "?")
        lines.append(f"• `{aid}`")
        lines.append(f"  _{prop.get('summary', '(no summary)')[:120]}_")
        lines.append(f"  Target: `{prop.get('target_path','?')}`  Tier: {prop.get('final_tier',3)}")
        if entry.get("downgrade_reason"):
            lines.append(f"  Downgrade: {entry['downgrade_reason']}")
        lines.append("")
    lines.append("Approve: `/growth_approve <id>` · Reject: `/growth_reject <id>`")
    await reply(update.message, "\n".join(lines))


async def cmd_growth_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    parts = (update.message.text or "").split(maxsplit=2)
    if len(parts) < 2:
        await update.message.reply_text("Usage: `/growth_approve <approval_id> [note]`", parse_mode="Markdown")
        return
    approval_id = parts[1]
    note = parts[2] if len(parts) >= 3 else None
    ok, msg = _resolve_growth_approval(approval_id, "approved", note)
    if ok:
        await reply(
            update.message,
            f"✅ Approved `{approval_id}`. {msg}\n\n"
            f"_Runs on next self_growth_weekly cycle, or manually: "
            f"`.venv/bin/python scripts/self_growth_weekly.py --apply-approved`._",
        )
    else:
        await update.message.reply_text(f"❌ {msg}")


async def cmd_growth_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    parts = (update.message.text or "").split(maxsplit=2)
    if len(parts) < 2:
        await update.message.reply_text("Usage: `/growth_reject <approval_id> [reason]`", parse_mode="Markdown")
        return
    approval_id = parts[1]
    reason = parts[2] if len(parts) >= 3 else None
    ok, msg = _resolve_growth_approval(approval_id, "rejected", reason)
    if ok:
        await reply(update.message, f"🚫 Rejected `{approval_id}`. {msg}")
    else:
        await update.message.reply_text(f"❌ {msg}")


# === Hackathon War Room commands ==============================================

async def _run_warroom_cli(args: list[str], timeout: int = 60) -> tuple[int, str]:
    return await run_cli(["scripts/hackathon_warroom.py", *args], timeout=timeout)


async def cmd_wr_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    parts = (update.message.text or "").split(maxsplit=2)
    if len(parts) < 2:
        await reply(
            update.message,
            "Usage: `/wr_start <slug>` — e.g. `/wr_start tata-steel-2026`\n"
            "Pre-fill input contract: edit `data/hackathons/<slug>/canonical_state.json` after start.",
        )
        return
    rc, output = await _run_warroom_cli(["start", parts[1]])
    await reply(update.message, f"{output[:3500]}\n\nExit: {rc}")


async def cmd_wr_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    parts = (update.message.text or "").split(maxsplit=2)
    if len(parts) < 2:
        hackathons_dir = Path(JARVIS_PROJECT_PATH) / "data" / "hackathons"
        if not hackathons_dir.exists():
            await update.message.reply_text("No active war rooms.")
            return
        slugs = [d.name for d in hackathons_dir.iterdir() if d.is_dir() and d.name != "_template"]
        if not slugs:
            await update.message.reply_text("No active war rooms.")
            return
        await reply(
            update.message,
            "*Active war rooms:*\n" + "\n".join(f"  • `{s}`" for s in slugs) +
            "\n\nUse `/wr_status <slug>` for detail.",
        )
        return
    rc, output = await _run_warroom_cli(["status", parts[1]])
    await reply(update.message, output[:3800])


async def _wr_run_bg(bot, chat_id: int, slug: str):
    """Long War Room phase — runs in a background task so the bot stays responsive."""
    rc, output = await _run_warroom_cli(["run", slug], timeout=1200)
    await send_to(bot, chat_id, f"🏁 War Room `{slug}` phase finished. Exit: {rc}\n\n{output[:3500]}")


async def cmd_wr_run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    parts = (update.message.text or "").split(maxsplit=2)
    if len(parts) < 2:
        await update.message.reply_text("Usage: `/wr_run <slug>`", parse_mode="Markdown")
        return
    slug = parts[1]
    await reply(update.message, f"⏳ Running next phase for `{slug}` (5-15 min) — I'll message when done. Bot stays responsive meanwhile.")
    context.application.create_task(_wr_run_bg(context.bot, update.effective_chat.id, slug))


async def cmd_wr_checkpoint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    parts = (update.message.text or "").split()
    if len(parts) < 3:
        await update.message.reply_text("Usage: `/wr_checkpoint <slug> <approve|drill|skip>`", parse_mode="Markdown")
        return
    rc, output = await _run_warroom_cli(["checkpoint", parts[1], parts[2]])
    await reply(update.message, f"{output[:3500]}\n\nExit: {rc}")


async def cmd_wr_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    parts = (update.message.text or "").split(maxsplit=2)
    if len(parts) < 3:
        await update.message.reply_text(
            "Usage: `/wr_pick <slug> <id1,id2,id3>` (Phase 2: 2-3 ids; Phase 3: 1 id)", parse_mode="Markdown")
        return
    rc, output = await _run_warroom_cli(["pick", parts[1], parts[2]])
    await reply(update.message, f"{output[:3500]}\n\nExit: {rc}")


# === LinkedIn pipeline commands (Tier-3 approval flow) ========================

def _parse_id_list(args: list[str]) -> list[str]:
    out: list[str] = []
    for tok in args:
        for piece in tok.split(","):
            piece = piece.strip()
            if piece:
                out.append(piece)
    return out


async def cmd_lp_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    if la is None:
        await update.message.reply_text("❌ LinkedIn module not available.")
        return
    try:
        await reply(update.message, la.status())
    except Exception as e:
        await update.message.reply_text(f"❌ /lp_status failed: {e}")


async def cmd_lp_approve_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    if la is None:
        await update.message.reply_text("❌ LinkedIn module not available.")
        return
    try:
        result = la.record_decision("approve_all")
        await reply(
            update.message,
            f"✅ All approved ({result.get('approved_count', 0)} items). "
            f"Executor runs at 10am IST, or `/lp_run` to execute now.",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ /lp_approve_all failed: {e}")


async def cmd_lp_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    if la is None:
        await update.message.reply_text("❌ LinkedIn module not available.")
        return
    ids = _parse_id_list(context.args or [])
    if not ids:
        await update.message.reply_text("Usage: `/lp_approve c0,c1,m0,p1`", parse_mode="Markdown")
        return
    try:
        result = la.record_decision("approve", ids)
        await reply(update.message, f"✅ Approved {len(ids)} items. Total this batch: {result.get('approved_count', 0)}")
    except Exception as e:
        await update.message.reply_text(f"❌ /lp_approve failed: {e}")


async def cmd_lp_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    if la is None:
        await update.message.reply_text("❌ LinkedIn module not available.")
        return
    ids = _parse_id_list(context.args or [])
    if not ids:
        await update.message.reply_text("Usage: `/lp_reject c0,c2,m4`", parse_mode="Markdown")
        return
    try:
        result = la.record_decision("reject", ids)
        await reply(update.message, f"🚫 Rejected {len(ids)} items. Total this batch: {result.get('rejected_count', 0)}")
    except Exception as e:
        await update.message.reply_text(f"❌ /lp_reject failed: {e}")


# Guard so two /lp_run can't race the same approval queue / LinkedIn session.
_lp_run_active = False


async def _lp_run_bg(bot, chat_id: int):
    global _lp_run_active
    try:
        proc = await asyncio.create_subprocess_exec(
            ".venv/bin/python", "-m", "scripts.linkedin.daily_runner", "execute",
            cwd=JARVIS_PROJECT_PATH,
            stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
        await send_to(bot, chat_id, f"✅ LinkedIn executor finished (exit {proc.returncode}).")
    except Exception as e:
        await send_to(bot, chat_id, f"❌ LinkedIn executor error: {e}")
    finally:
        _lp_run_active = False


async def cmd_lp_run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    global _lp_run_active
    if _lp_run_active:
        await update.message.reply_text("⏳ LinkedIn executor already running — wait for it to finish.")
        return
    _lp_run_active = True
    await update.message.reply_text("🚀 Triggering LinkedIn executor on approved items…")
    context.application.create_task(_lp_run_bg(context.bot, update.effective_chat.id))


async def cmd_lp_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    if lp_reporter is None:
        await update.message.reply_text("❌ LinkedIn reporter not available.")
        return
    try:
        await reply(update.message, lp_reporter.build_report())
    except Exception as e:
        await update.message.reply_text(f"❌ /lp_report failed: {e}")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    if not VOICE_ENABLED:
        await update.message.reply_text("Voice messages not supported (voice_handler not loaded).")
        return
    await _handle_voice_message(update, context, call_claude_fn=call_claude, send_voice_reply=True)


# === Global error handler =====================================================

async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    tb = "".join(traceback.format_exception(type(context.error), context.error, context.error.__traceback__))
    log.error("Handler exception: %s\n%s", context.error, tb)
    try:
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                f"⚠️ Internal error: {type(context.error).__name__}. Logged — try again."
            )
    except Exception:
        pass


# === Startup ==================================================================

_relay_task = None  # module ref so the background task isn't garbage-collected


async def post_init(app: Application):
    global _relay_task
    _load_pending()
    if BOSS_CHAT_ID is None:
        log.warning("BOSS_CHAT_ID unset — WhatsApp relay disabled (set ALLOWED_USER_IDS).")
    else:
        # plain asyncio task (avoids PTB's "app not running" create_task warning);
        # module-level ref keeps it alive for the daemon's lifetime.
        _relay_task = asyncio.create_task(wa_relay_loop(app))
        log.info("WhatsApp relay enabled → Boss chat %s", BOSS_CHAT_ID)


async def post_shutdown(app: Application):
    """Cancel the relay task so it isn't 'destroyed while pending'. Non-blocking —
    we request cancellation but never await it (awaiting can hang shutdown)."""
    global _relay_task
    if _relay_task and not _relay_task.done():
        _relay_task.cancel()


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set in .env")
    if not ALLOWED_USER_IDS:
        raise RuntimeError("ALLOWED_USER_IDS not set — refusing to start an open relay")

    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # Built-in
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # WhatsApp relay
    app.add_handler(CommandHandler("wa_pending", cmd_wa_pending))
    app.add_handler(CommandHandler("wa_reply", cmd_wa_reply))
    app.add_handler(CommandHandler("wa_ignore", cmd_wa_ignore))

    # Autonomous goals
    app.add_handler(CommandHandler("goal_add", cmd_goal_add))
    app.add_handler(CommandHandler("goals", cmd_goals))
    app.add_handler(CommandHandler("goal_status", cmd_goal_status))
    app.add_handler(CommandHandler("goal_approve", cmd_goal_approve))
    app.add_handler(CommandHandler("goal_reject", cmd_goal_reject))
    app.add_handler(CommandHandler("digest_now", cmd_digest_now))

    # Self-growth
    app.add_handler(CommandHandler("growth_list", cmd_growth_list))
    app.add_handler(CommandHandler("growth_approve", cmd_growth_approve))
    app.add_handler(CommandHandler("growth_reject", cmd_growth_reject))

    # Hackathon War Room
    app.add_handler(CommandHandler("wr_start", cmd_wr_start))
    app.add_handler(CommandHandler("wr_status", cmd_wr_status))
    app.add_handler(CommandHandler("wr_run", cmd_wr_run))
    app.add_handler(CommandHandler("wr_checkpoint", cmd_wr_checkpoint))
    app.add_handler(CommandHandler("wr_pick", cmd_wr_pick))

    # LinkedIn
    app.add_handler(CommandHandler("lp_status", cmd_lp_status))
    app.add_handler(CommandHandler("lp_approve_all", cmd_lp_approve_all))
    app.add_handler(CommandHandler("lp_approve", cmd_lp_approve))
    app.add_handler(CommandHandler("lp_reject", cmd_lp_reject))
    app.add_handler(CommandHandler("lp_run", cmd_lp_run))
    app.add_handler(CommandHandler("lp_report", cmd_lp_report))

    # Jarvis slash commands → Claude
    for cmd in SLASH_ALIASES.keys():
        app.add_handler(CommandHandler(cmd, handle_slash))

    # WhatsApp reply-capture runs BEFORE the general text handler (group -1).
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, wa_reply_capture), group=-1)
    # All other text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Voice
    if VOICE_ENABLED:
        app.add_handler(MessageHandler(filters.VOICE, handle_voice))
        log.info("Voice messages: ENABLED (Whisper STT + Piper TTS)")
    else:
        log.info("Voice messages: DISABLED (voice_handler import failed)")

    app.add_error_handler(on_error)

    log.info("🤖 Jarvis Telegram bridge starting…")
    log.info("Project: %s", JARVIS_PROJECT_PATH)
    log.info("Authorized users: %s", ALLOWED_USER_IDS)

    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
