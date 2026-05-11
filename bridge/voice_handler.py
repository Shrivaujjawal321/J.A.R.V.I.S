"""
Telegram voice message handler for Jarvis bridge.

When Boss sends a voice message (OGG/Opus) via Telegram:
  1. Download the OGG file
  2. Convert OGG -> WAV via gstreamer (gst-launch-1.0, no ffmpeg needed)
  3. Transcribe via Whisper
  4. Echo transcript back so Boss can confirm
  5. Run transcript through Jarvis (same call_claude() as text messages)
  6. Optionally synthesize reply via Piper TTS + send back as voice note

This module is imported by telegram_bridge.py as a parallel branch.
It does NOT modify any existing text-message handling.

Requirements:
    pip install openai-whisper (in project venv)
    gst-launch-1.0 with oggdemux + opusdec plugins (system, usually pre-installed)

GStreamer pipeline used:
    filesrc -> oggdemux -> opusdec -> audioconvert ->
    audio/x-raw,format=S16LE,channels=1,rate=16000 -> wavenc -> filesink

Privacy note:
    Voice OGG files are saved temporarily in data/voice/recordings/tg-{ts}.ogg
    and converted WAVs at data/voice/recordings/tg-{ts}.wav.
    They are NOT auto-deleted — purge manually if needed.
"""

import asyncio
import json
import subprocess
import sys
import time
import warnings
from pathlib import Path

JARVIS_ROOT = Path(__file__).parent.parent
VENV_PYTHON = JARVIS_ROOT / ".venv" / "bin" / "python"
RECORDINGS_DIR = JARVIS_ROOT / "data" / "voice" / "recordings"
SCRIPTS_VOICE = JARVIS_ROOT / "scripts" / "voice"
WHISPER_MODEL_SIZE = "base"


def _convert_ogg_to_wav(ogg_path: Path, wav_path: Path) -> bool:
    """
    Convert OGG/Opus audio to 16kHz mono WAV using gstreamer.

    Returns True on success.
    GStreamer must have oggdemux + opusdec + audioconvert + wavenc plugins.
    """
    pipeline = (
        f"filesrc location={ogg_path} ! "
        "oggdemux ! opusdec ! audioconvert ! "
        "audio/x-raw,format=S16LE,channels=1,rate=16000 ! "
        f"wavenc ! filesink location={wav_path}"
    )
    result = subprocess.run(
        ["gst-launch-1.0", "-q"] + pipeline.split(),
        capture_output=True,
        timeout=30,
    )
    return result.returncode == 0 and wav_path.exists()


def _transcribe_wav(wav_path: Path) -> str:
    """
    Transcribe a WAV file via Whisper.

    Invokes transcribe.py as subprocess so the heavy model loading
    happens in a separate process and doesn't block the async bridge event loop.
    """
    result = subprocess.run(
        [str(VENV_PYTHON), str(SCRIPTS_VOICE / "transcribe.py"),
         "--input", str(wav_path),
         "--model", WHISPER_MODEL_SIZE],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Transcription failed: {result.stderr[:500]}")
    return result.stdout.strip()


def _synthesize_to_ogg(text: str, ogg_path: Path) -> bool:
    """
    Synthesize text to speech (WAV via Piper) then convert WAV -> OGG/Opus
    using gstreamer, for sending back as a Telegram voice note.

    Returns True on success.
    """
    import tempfile

    ts = int(time.time())
    tmp_wav = RECORDINGS_DIR / f"tts-reply-{ts}.wav"

    # Step 1: Piper TTS -> WAV
    speak_result = subprocess.run(
        [str(VENV_PYTHON), str(SCRIPTS_VOICE / "speak.py"),
         "--text", text[:800],
         "--output", str(tmp_wav)],
        capture_output=True,
        timeout=60,
    )
    if speak_result.returncode != 0 or not tmp_wav.exists():
        return False

    # Step 2: WAV -> OGG/Opus via gstreamer
    pipeline = (
        f"filesrc location={tmp_wav} ! wavparse ! audioconvert ! "
        f"opusenc ! oggmux ! filesink location={ogg_path}"
    )
    gst_result = subprocess.run(
        ["gst-launch-1.0", "-q"] + pipeline.split(),
        capture_output=True,
        timeout=30,
    )

    # Cleanup temp WAV
    try:
        tmp_wav.unlink()
    except Exception:
        pass

    return gst_result.returncode == 0 and ogg_path.exists()


async def handle_voice_message(
    update,
    context,
    call_claude_fn,
    send_voice_reply: bool = True,
) -> None:
    """
    Handle a Telegram voice message.

    Args:
        update: Telegram Update object
        context: Telegram ContextTypes.DEFAULT_TYPE
        call_claude_fn: Async callable(prompt: str) -> str (from telegram_bridge.py)
        send_voice_reply: If True, synthesize reply and send as voice note
    """
    from telegram.constants import ChatAction

    RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
    ts = int(time.time())

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING,
    )

    # --- Step 1: Download OGG ---
    voice = update.message.voice
    ogg_path = RECORDINGS_DIR / f"tg-{ts}.ogg"
    wav_path = RECORDINGS_DIR / f"tg-{ts}.wav"

    try:
        tg_file = await context.bot.get_file(voice.file_id)
        await tg_file.download_to_drive(str(ogg_path))
    except Exception as e:
        await update.message.reply_text(f"Could not download voice message: {e}")
        return

    # --- Step 2: Convert OGG -> WAV ---
    try:
        ok = await asyncio.get_event_loop().run_in_executor(
            None, _convert_ogg_to_wav, ogg_path, wav_path
        )
    except Exception as e:
        await update.message.reply_text(f"Audio conversion failed: {e}")
        return

    if not ok:
        await update.message.reply_text(
            "Could not convert voice message. "
            "Make sure gst-launch-1.0 with OGG/Opus plugins is installed."
        )
        return

    # --- Step 3: Transcribe ---
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING,
    )

    try:
        transcript = await asyncio.get_event_loop().run_in_executor(
            None, _transcribe_wav, wav_path
        )
    except Exception as e:
        await update.message.reply_text(f"Transcription failed: {e}")
        return

    if not transcript:
        await update.message.reply_text("(Could not understand audio. Please try again.)")
        return

    # --- Step 4: Echo transcript back ---
    await update.message.reply_text(
        f"I heard: \"{transcript}\"",
        parse_mode="Markdown",
    )

    # --- Step 5: Run through Jarvis ---
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING,
    )

    reply = await call_claude_fn(transcript)

    # Send text reply
    for i in range(0, len(reply), 4000):
        await update.message.reply_text(reply[i:i + 4000], parse_mode="Markdown")

    # --- Step 6: Optional voice reply ---
    if send_voice_reply:
        reply_ogg = RECORDINGS_DIR / f"tg-reply-{ts}.ogg"
        try:
            ok = await asyncio.get_event_loop().run_in_executor(
                None, _synthesize_to_ogg, reply[:800], reply_ogg
            )
            if ok:
                with open(reply_ogg, "rb") as audio_file:
                    await update.message.reply_voice(voice=audio_file)
        except Exception as e:
            # Voice reply is optional — don't fail the whole handler
            pass
