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
