#!/usr/bin/env python3
"""
Piper TTS speech synthesis for Jarvis.

Converts text to speech using Piper TTS (ONNX-based, no API key).
Plays audio via aplay (ALSA) or saves to a WAV file.

Voice model is downloaded from HuggingFace on first use (~61MB for lessac-medium).
Downloaded models are stored in data/voice/models/.

Usage:
    python speak.py --text "Hello Boss, Jarvis online"
    python speak.py --input reply.txt
    python speak.py --text "Hello" --output /tmp/out.wav
    python speak.py --text "Hello" --voice en_US-lessac-medium
"""

import argparse
import subprocess
import sys
import time
import wave
from pathlib import Path

MODELS_DIR = Path(__file__).parents[2] / "data" / "voice" / "models"
DEFAULT_VOICE = "en_US-lessac-medium"
VENV_BIN = Path(__file__).parents[2] / ".venv" / "bin"


def ensure_voice_model(voice_name: str) -> tuple[Path, Path]:
    """
    Ensure the voice ONNX model and config are present.
    Downloads from HuggingFace if not found.

    Returns (model_path, config_path).
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODELS_DIR / f"{voice_name}.onnx"
    config_path = MODELS_DIR / f"{voice_name}.onnx.json"

    if not model_path.exists() or not config_path.exists():
        print(f"Downloading voice model '{voice_name}' (~61MB)...", file=sys.stderr, flush=True)
        from piper.download_voices import download_voice
        download_voice(voice_name, MODELS_DIR)
        print("Voice model downloaded.", file=sys.stderr, flush=True)

    return model_path, config_path


def synthesize_to_wav(
    text: str,
    voice_name: str = DEFAULT_VOICE,
    output_path: Path | None = None,
) -> Path:
    """
    Synthesize text to WAV using Piper.

    If output_path is None, writes to a temp file in data/voice/recordings/.
    Returns the path to the WAV file.
    """
    import tempfile
    import os

    model_path, config_path = ensure_voice_model(voice_name)

    if output_path is None:
        tmpdir = Path(__file__).parents[2] / "data" / "voice" / "recordings"
        tmpdir.mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        output_path = tmpdir / f"tts-{ts}.wav"

    piper_bin = VENV_BIN / "piper"
    if not piper_bin.exists():
        piper_bin = Path("piper")  # fallback to PATH

    cmd = [
        str(piper_bin),
        "-m", str(model_path),
        "-c", str(config_path),
        "-f", str(output_path),
    ]

    result = subprocess.run(
        cmd,
        input=text.encode("utf-8"),
        capture_output=True,
    )

    if result.returncode != 0:
        print(f"ERROR: Piper failed: {result.stderr.decode()}", file=sys.stderr)
        sys.exit(1)

    return output_path


def play_wav(wav_path: Path) -> None:
    """Play a WAV file via aplay (ALSA, no PortAudio needed)."""
    result = subprocess.run(
        ["aplay", "-q", str(wav_path)],
        capture_output=True,
    )
    if result.returncode != 0:
        print(f"WARNING: aplay error: {result.stderr.decode()}", file=sys.stderr)


def speak(
    text: str,
    voice_name: str = DEFAULT_VOICE,
    output_path: Path | None = None,
) -> Path | None:
    """
    Synthesize and optionally play text.

    If output_path is provided, saves to that path and does NOT play.
    If output_path is None, plays directly and cleans up temp file.
    Returns output_path if saved, else None.
    """
    import tempfile
    import os

    if output_path:
        # Save mode — synthesize to user-specified path
        wav_path = synthesize_to_wav(text, voice_name, output_path=output_path)
        return wav_path
    else:
        # Play mode — synthesize to temp, play, then keep in recordings for review
        wav_path = synthesize_to_wav(text, voice_name, output_path=None)
        play_wav(wav_path)
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Piper TTS for Jarvis")

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--text", "-t",
        type=str,
        help="Text to speak",
    )
    input_group.add_argument(
        "--input", "-i",
        type=str,
        help="Path to text file to speak",
    )

    parser.add_argument(
        "--voice",
        default=DEFAULT_VOICE,
        help=f"Piper voice name (default: {DEFAULT_VOICE})",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output WAV path. If omitted, plays directly via aplay.",
    )
    args = parser.parse_args()

    if args.text:
        text = args.text.strip()
    else:
        text_path = Path(args.input)
        if not text_path.exists():
            print(f"ERROR: File not found: {text_path}", file=sys.stderr)
            sys.exit(1)
        text = text_path.read_text(encoding="utf-8").strip()

    if not text:
        print("ERROR: Empty text.", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else None
    saved = speak(text, voice_name=args.voice, output_path=output_path)

    if saved:
        print(f"Saved: {saved}")


if __name__ == "__main__":
    main()
