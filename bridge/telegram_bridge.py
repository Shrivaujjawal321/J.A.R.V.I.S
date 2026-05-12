"""
Telegram Bridge for Jarvis.

This script listens to your Telegram bot and forwards messages to Claude Code
in headless mode. Response goes back to Telegram.

Run as background service (systemd / launchd / pm2 / nohup).

Setup:
1. Create bot at @BotFather on Telegram, get token
2. cp .env.example .env, add TELEGRAM_BOT_TOKEN
3. pip install -r requirements.txt
4. python telegram_bridge.py
"""

import asyncio
import json
import os
import subprocess
from pathlib import Path

import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
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

# === Configuration ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
JARVIS_PROJECT_PATH = os.getenv("JARVIS_PROJECT_PATH", str(Path(__file__).parent.parent))
ALLOWED_USER_IDS = [int(x) for x in os.getenv("ALLOWED_USER_IDS", "").split(",") if x]
CLAUDE_TIMEOUT = int(os.getenv("CLAUDE_TIMEOUT", "180"))  # seconds
MAX_TURNS = int(os.getenv("MAX_TURNS", "15"))

# jarvis-core daemon (Phase 1: text via super-agent orchestrator)
JARVIS_CORE_URL = os.getenv("JARVIS_CORE_URL", "http://127.0.0.1:8765")
USE_DAEMON = os.getenv("JARVIS_USE_DAEMON", "1") != "0"


def is_authorized(user_id: int) -> bool:
    """Only allow specific Telegram user IDs to use this bot."""
    if not ALLOWED_USER_IDS:
        return True  # No restriction set (be careful in production)
    return user_id in ALLOWED_USER_IDS


async def _call_via_subprocess(prompt: str) -> str:
    """Legacy fallback: spawn `claude` CLI directly. Used when daemon is down."""
    cmd = [
        "claude",
        "-p", prompt,
        "--output-format", "json",
        "--max-turns", str(MAX_TURNS),
    ]
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=JARVIS_PROJECT_PATH,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=CLAUDE_TIMEOUT
        )
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
    """Phase 1 path: send to jarvis-core daemon over HTTP."""
    try:
        async with httpx.AsyncClient(timeout=CLAUDE_TIMEOUT) as client:
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
            reply = data.get("reply") or "(empty reply from jarvis-core)"
            return reply
    except (httpx.ConnectError, httpx.ReadTimeout) as e:
        # Daemon down / slow — fall back to direct subprocess
        print(f"⚠️  jarvis-core unreachable ({type(e).__name__}), falling back to subprocess")
        return await _call_via_subprocess(prompt)
    except Exception as e:
        return f"❌ jarvis-core error: {type(e).__name__}: {e}"


async def call_claude(prompt: str, user_id: int = 0) -> str:
    """Dispatch to jarvis-core daemon if enabled, else direct subprocess."""
    if USE_DAEMON:
        return await _call_via_daemon(prompt, user_id=user_id)
    return await _call_via_subprocess(prompt)


# === Telegram Handlers ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("Sorry, this bot is private.")
        return

    await update.message.reply_text(
        "👋 Jarvis here. Type anything — I'll handle it.\n\n"
        "Try:\n"
        "• 'What's my schedule today?'\n"
        "• 'Triage my inbox'\n"
        "• '/briefing'\n"
        "• 'Add task: call mom tomorrow'"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Available slash commands:\n"
        "/briefing — morning briefing\n"
        "/triage — process inbox\n"
        "/plan-day — plan today\n"
        "/weekly-review — weekly review\n\n"
        "Or just type naturally!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return

    user_message = update.message.text

    # Show typing indicator
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing",
    )

    # Call Claude Code via jarvis-core daemon (Phase 1) or subprocess fallback
    response = await call_claude(user_message, user_id=update.effective_user.id)

    # Telegram message limit is 4096 chars — split if needed
    for chunk in chunks(response, 4000):
        await update.message.reply_text(chunk, parse_mode="Markdown")


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

    raw = update.message.text.lstrip("/").split("@", 1)[0].split()[0]
    cmd = SLASH_ALIASES.get(raw, f"/{raw}")
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing",
    )

    response = await call_claude(cmd, user_id=update.effective_user.id)

    for chunk in chunks(response, 4000):
        await update.message.reply_text(chunk, parse_mode="Markdown")


def chunks(text: str, size: int):
    """Yield successive chunks of given size."""
    for i in range(0, len(text), size):
        yield text[i : i + size]


# === Phase 3: Autonomous goal commands ===
# Telegram /goal_add, /goals, /goal_status, /goal_approve, /goal_reject, /digest_now


async def _post_json(path: str, payload: dict) -> dict:
    async with httpx.AsyncClient(timeout=CLAUDE_TIMEOUT) as client:
        r = await client.post(f"{JARVIS_CORE_URL}{path}", json=payload)
        r.raise_for_status()
        return r.json()


async def _get_json(path: str, params: dict | None = None) -> dict:
    async with httpx.AsyncClient(timeout=CLAUDE_TIMEOUT) as client:
        r = await client.get(f"{JARVIS_CORE_URL}{path}", params=params or {})
        r.raise_for_status()
        return r.json()


async def cmd_goal_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    description = (update.message.text or "").split(maxsplit=1)
    if len(description) < 2:
        await update.message.reply_text(
            "Usage: `/goal_add <description>`\n"
            "Example: `/goal_add research 3 papers on prompt caching, summarize each in 5 bullets`",
            parse_mode="Markdown",
        )
        return
    try:
        result = await _post_json(
            "/goal",
            {
                "user_id": str(update.effective_user.id),
                "description": description[1].strip(),
            },
        )
        await update.message.reply_text(
            f"🎯 Goal queued: `{result['goal_id']}`\n"
            f"Status: `{result['status']}`\n"
            f"Scheduler will pick it up within 60s. Track with `/goal_status {result['goal_id']}`.",
            parse_mode="Markdown",
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
        await update.message.reply_text("No goals yet. Use `/goal_add <description>` to start.")
        return
    lines = ["📋 *Recent goals* (most recent first)"]
    for g in goals[:15]:
        emoji = {
            "queued": "🕒",
            "planning": "🧩",
            "running": "🏃",
            "awaiting_approval": "🔐",
            "completed": "✅",
            "failed": "⚠️",
            "cancelled": "❌",
        }.get(g["status"], "•")
        desc = (g["description"][:80] + "…") if len(g["description"]) > 80 else g["description"]
        lines.append(f"{emoji} `{g['goal_id']}` · _{g['status']}_ · {desc}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


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
    await update.message.reply_text("\n".join(lines)[:3900], parse_mode="Markdown")


async def cmd_goal_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    parts = (update.message.text or "").split(maxsplit=2)
    if len(parts) < 2:
        await update.message.reply_text(
            "Usage: `/goal_approve <approval_id> [note]`", parse_mode="Markdown"
        )
        return
    approval_id = parts[1]
    note = parts[2] if len(parts) >= 3 else None
    try:
        result = await _post_json(
            f"/approval/{approval_id}/decide",
            {
                "decision": "approved",
                "boss_note": note,
                "decided_by": str(update.effective_user.id),
            },
        )
        await update.message.reply_text(
            f"✅ Approved `{approval_id}` — resumed={result.get('resumed', False)}",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Could not approve: {e}")


async def cmd_goal_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    parts = (update.message.text or "").split(maxsplit=2)
    if len(parts) < 2:
        await update.message.reply_text(
            "Usage: `/goal_reject <approval_id> [reason]`", parse_mode="Markdown"
        )
        return
    approval_id = parts[1]
    note = parts[2] if len(parts) >= 3 else None
    try:
        result = await _post_json(
            f"/approval/{approval_id}/decide",
            {
                "decision": "rejected",
                "boss_note": note,
                "decided_by": str(update.effective_user.id),
            },
        )
        await update.message.reply_text(
            f"❌ Rejected `{approval_id}` — resumed={result.get('resumed', False)}",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Could not reject: {e}")


async def cmd_digest_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """On-demand digest (vs the cron one at 06:30 IST)."""
    if not is_authorized(update.effective_user.id):
        return
    try:
        import subprocess
        result = subprocess.run(
            [".venv/bin/python", "scripts/morning_digest.py", "--stdout", "--hours", "24"],
            cwd=JARVIS_PROJECT_PATH,
            capture_output=True, text=True, timeout=20,
        )
        text = result.stdout or result.stderr or "(no output)"
        for chunk in chunks(text, 4000):
            await update.message.reply_text(chunk, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Could not render digest: {e}")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming voice messages — parallel branch, does not touch text flow."""
    if not is_authorized(update.effective_user.id):
        return

    if not VOICE_ENABLED:
        await update.message.reply_text(
            "Voice messages not supported (voice_handler not loaded)."
        )
        return

    await _handle_voice_message(
        update,
        context,
        call_claude_fn=call_claude,
        send_voice_reply=True,
    )


# === Main ===

def main():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set in .env")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Built-in commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Phase 3: autonomous goal commands (direct daemon HTTP, not Claude)
    app.add_handler(CommandHandler("goal_add", cmd_goal_add))
    app.add_handler(CommandHandler("goals", cmd_goals))
    app.add_handler(CommandHandler("goal_status", cmd_goal_status))
    app.add_handler(CommandHandler("goal_approve", cmd_goal_approve))
    app.add_handler(CommandHandler("goal_reject", cmd_goal_reject))
    app.add_handler(CommandHandler("digest_now", cmd_digest_now))

    # Jarvis slash commands — forward to Claude Code
    for cmd in SLASH_ALIASES.keys():
        app.add_handler(CommandHandler(cmd, handle_slash))

    # All other text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Voice messages (parallel branch — does not affect text handling)
    if VOICE_ENABLED:
        app.add_handler(MessageHandler(filters.VOICE, handle_voice))
        print("   Voice messages: ENABLED (Whisper STT + Piper TTS)")
    else:
        print("   Voice messages: DISABLED (voice_handler import failed)")

    print("🤖 Jarvis Telegram bridge starting...")
    print(f"   Project: {JARVIS_PROJECT_PATH}")
    print(f"   Authorized users: {ALLOWED_USER_IDS or 'ALL (set ALLOWED_USER_IDS!)'}")

    app.run_polling()


if __name__ == "__main__":
    main()
