#!/usr/bin/env python3
"""
Full local voice loop for Jarvis.

Hands-free conversation: speak -> Whisper STT -> Claude -> Piper TTS -> aplay.

Flow per turn:
  1. Press Enter to start recording (or 'q' to quit)
  2. Speak — silence detection stops recording after 2s quiet (or Ctrl+C)
  3. Transcription displayed on screen (Whisper)
  4. Claude CLI invoked headlessly with the transcript
  5. Reply spoken aloud via Piper TTS + aplay
  6. Turn logged to data/voice/transcripts/{date}.jsonl
  7. Loop

Privacy note:
  Recordings are saved to data/voice/recordings/ on disk.
  Transcripts logged to data/voice/transcripts/{date}.jsonl.
  To purge: rm data/voice/recordings/*.wav data/voice/transcripts/*.jsonl

Usage:
    python voice_loop.py
    python voice_loop.py --no-speak  (text-only, no TTS)
    python voice_loop.py --max-seconds 60
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

JARVIS_ROOT = Path(__file__).parents[2]
SCRIPTS_VOICE = JARVIS_ROOT / "scripts" / "voice"
TRANSCRIPTS_DIR = JARVIS_ROOT / "data" / "voice" / "transcripts"
LOGS_DIR = JARVIS_ROOT / "data" / "logs"
MARKERS_DIR = JARVIS_ROOT / "data" / "markers"
VENV_PYTHON = JARVIS_ROOT / ".venv" / "bin" / "python"

MAX_REPLY_CHARS = 800  # truncate long replies before TTS


def dev_mode_active() -> bool:
    """Return True if Boss has set dev_mode_active marker (suppress voice output)."""
    return (MARKERS_DIR / "dev_mode_active").exists()


def record_audio(output_path: Path, max_seconds: int = 30) -> Path:
    """Invoke record.py as subprocess. Returns path to WAV."""
    result = subprocess.run(
        [str(VENV_PYTHON), str(SCRIPTS_VOICE / "record.py"),
         "--max-seconds", str(max_seconds),
         "--output", str(output_path)],
        capture_output=False,  # let record.py print to terminal
    )
    if result.returncode != 0:
        raise RuntimeError("Recording failed")
    return output_path


def transcribe_audio(wav_path: Path) -> str:
    """Invoke transcribe.py, return plain text."""
    result = subprocess.run(
        [str(VENV_PYTHON), str(SCRIPTS_VOICE / "transcribe.py"),
         "--input", str(wav_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Transcription failed: {result.stderr}")
    return result.stdout.strip()


def call_claude(prompt: str, max_turns: int = 20) -> str:
    """
    Invoke Claude CLI headlessly. Returns reply text.

    Runs: claude -p "<prompt>" --output-format json --max-turns 20
    """
    cmd = [
        "claude",
        "-p", prompt,
        "--output-format", "json",
        "--max-turns", str(max_turns),
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(JARVIS_ROOT),
            timeout=180,
        )
        if result.returncode != 0:
            return f"Jarvis error: {result.stderr[:300]}"

        try:
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                return data.get("result") or data.get("response") or str(data)[:2000]
            return str(data)[:2000]
        except json.JSONDecodeError:
            return result.stdout.strip()[:2000]

    except subprocess.TimeoutExpired:
        return "Jarvis timed out. Try a simpler request."
    except Exception as e:
        return f"Error reaching Jarvis: {e}"


def speak_text(text: str, voice: str = "en_US-lessac-medium") -> None:
    """Invoke speak.py to synthesize and play text."""
    # Truncate to avoid very long TTS
    truncated = text[:MAX_REPLY_CHARS]
    if len(text) > MAX_REPLY_CHARS:
        truncated += "... (reply truncated for speech)"

    subprocess.run(
        [str(VENV_PYTHON), str(SCRIPTS_VOICE / "speak.py"),
         "--text", truncated,
         "--voice", voice],
        capture_output=False,
    )


def log_turn(
    turn: int,
    transcript: str,
    reply: str,
    wav_path: Path,
    latency_s: float,
) -> None:
    """Append turn to JSONL log files."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "turn": turn,
        "user": transcript,
        "jarvis": reply,
        "wav": str(wav_path),
        "latency_s": round(latency_s, 2),
    }

    # Daily transcript log
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    transcript_file = TRANSCRIPTS_DIR / f"{date_str}.jsonl"
    with open(transcript_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Global voice loop log
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    loop_log = LOGS_DIR / "voice_loop.jsonl"
    with open(loop_log, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis voice loop")
    parser.add_argument(
        "--max-seconds",
        type=int,
        default=30,
        help="Max recording duration per turn (default: 30)",
    )
    parser.add_argument(
        "--no-speak",
        action="store_true",
        help="Disable TTS output (text only)",
    )
    parser.add_argument(
        "--voice",
        default="en_US-lessac-medium",
        help="Piper voice name",
    )
    args = parser.parse_args()

    print("=" * 60)
    print(" Jarvis Voice Interface")
    print("=" * 60)
    print("Press Enter to speak, 'q' + Enter to quit, Ctrl+C to exit.")
    print()

    if dev_mode_active():
        print("[DEV MODE: voice output suppressed]")

    turn = 0
    while True:
        try:
            user_input = input("Press Enter to talk (or 'q' to quit)... ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if user_input == "q":
            print("Goodbye.")
            break

        turn += 1
        t_start = time.time()

        # --- Step 1: Record ---
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        wav_path = JARVIS_ROOT / "data" / "voice" / "recordings" / f"in-{ts}.wav"
        try:
            record_audio(wav_path, max_seconds=args.max_seconds)
        except RuntimeError as e:
            print(f"Recording error: {e}")
            continue

        # --- Step 2: Transcribe ---
        print("Transcribing...", end=" ", flush=True)
        try:
            transcript = transcribe_audio(wav_path)
        except RuntimeError as e:
            print(f"\nTranscription error: {e}")
            continue

        print(f"\nYou said: {transcript}")

        if not transcript:
            print("(No speech detected. Try again.)")
            continue

        # --- Step 3: Ask Claude ---
        print("Jarvis thinking...", flush=True)
        reply = call_claude(transcript)
        print(f"\nJarvis: {reply}\n")

        t_latency = time.time() - t_start

        # --- Step 4: Log turn ---
        log_turn(turn, transcript, reply, wav_path, t_latency)

        # --- Step 5: Speak reply ---
        if not args.no_speak and not dev_mode_active():
            speak_text(reply, voice=args.voice)

        print(f"[Turn {turn} | {t_latency:.1f}s total]")
        print()


if __name__ == "__main__":
    main()
