#!/usr/bin/env python3
"""
Whisper STT transcription for Jarvis.

Transcribes a WAV file using OpenAI Whisper.
Loads the model from ~/.cache/whisper/ (downloaded on first use, ~139MB for 'base').

Audio is loaded via scipy (no ffmpeg required for WAV files).

Usage:
    python transcribe.py --input recording.wav
    python transcribe.py --input recording.wav --model small --language hi
    python transcribe.py --input recording.wav --json
"""

import argparse
import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np

VENV_PYTHON = Path(__file__).parents[2] / ".venv" / "bin" / "python"
SAMPLE_RATE = 16000  # Whisper's native sample rate


def load_wav_as_float32(wav_path: Path) -> np.ndarray:
    """
    Load a WAV file as float32 numpy array in [-1.0, 1.0].

    Handles sample rate conversion to 16kHz if needed.
    No ffmpeg required.
    """
    import scipy.io.wavfile as wav_io
    from scipy.signal import resample_poly
    import math

    file_rate, data = wav_io.read(str(wav_path))

    # Stereo -> mono
    if data.ndim == 2:
        data = data.mean(axis=1)

    # Convert to float32 in [-1, 1]
    if data.dtype == np.int16:
        audio = data.astype(np.float32) / 32768.0
    elif data.dtype == np.int32:
        audio = data.astype(np.float32) / 2147483648.0
    elif data.dtype == np.float32:
        audio = data
    else:
        audio = data.astype(np.float32)

    # Resample to 16kHz if needed
    if file_rate != SAMPLE_RATE:
        # Find GCD for clean rational resample ratio
        g = math.gcd(SAMPLE_RATE, file_rate)
        up = SAMPLE_RATE // g
        down = file_rate // g
        audio = resample_poly(audio, up, down).astype(np.float32)

    return audio


def transcribe(
    wav_path: Path,
    model_size: str = "base",
    language: str | None = None,
) -> dict:
    """
    Transcribe a WAV file with Whisper.

    Returns Whisper's result dict with 'text', 'segments', 'language' keys.
    """
    import whisper

    # Suppress FP16 warning — expected on CPU
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        model = whisper.load_model(model_size)

    audio = load_wav_as_float32(wav_path)

    kwargs: dict = {}
    if language and language.lower() != "auto":
        kwargs["language"] = language

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        result = model.transcribe(audio, **kwargs)

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Whisper STT transcription for Jarvis")
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to input WAV file",
    )
    parser.add_argument(
        "--model", "-m",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base, ~139MB)",
    )
    parser.add_argument(
        "--language", "-l",
        default="auto",
        help="Language code (e.g. 'en', 'hi') or 'auto' for auto-detect (default: auto)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output full JSON result instead of plain text",
    )
    args = parser.parse_args()

    wav_path = Path(args.input)
    if not wav_path.exists():
        print(f"ERROR: File not found: {wav_path}", file=sys.stderr)
        sys.exit(1)

    # Inform user about first-time model download
    import whisper as _w
    import os
    cache_dir = Path(os.path.expanduser("~/.cache/whisper"))
    model_file = cache_dir / f"{args.model}.pt"
    if not model_file.exists():
        print(f"Downloading Whisper '{args.model}' model (~139MB for base)...", file=sys.stderr, flush=True)

    t0 = time.time()
    result = transcribe(wav_path, model_size=args.model, language=args.language)
    elapsed = time.time() - t0

    print(f"[transcribe] {elapsed:.2f}s", file=sys.stderr, flush=True)

    if args.json:
        # Return JSON without non-serializable numpy types
        output = {
            "text": result["text"].strip(),
            "language": result.get("language", "unknown"),
            "duration_s": elapsed,
        }
        print(json.dumps(output, ensure_ascii=False))
    else:
        # Clean plain text output — pipes cleanly
        print(result["text"].strip())


if __name__ == "__main__":
    main()
