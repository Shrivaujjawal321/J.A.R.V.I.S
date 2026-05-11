#!/usr/bin/env python3
"""
Push-to-talk voice recorder for Jarvis.

Records audio from the default microphone using arecord (ALSA).
Stops on Ctrl+C or when silence (< threshold dB) is detected for 2 seconds,
or when max_seconds is reached.

Usage:
    python record.py
    python record.py --max-seconds 60
    python record.py --output /path/to/out.wav
"""

import argparse
import os
import signal
import subprocess
import sys
import tempfile
import time
import wave
from datetime import datetime
from pathlib import Path

import numpy as np

SAMPLE_RATE = 16000
SAMPLE_WIDTH = 2  # 16-bit = 2 bytes
CHANNELS = 1
SILENCE_THRESHOLD_DB = -40  # dB: below this = silence
SILENCE_DURATION = 2.0  # seconds of silence before stopping
CHUNK_SECONDS = 0.1  # analysis chunk size

RECORDINGS_DIR = Path(__file__).parents[2] / "data" / "voice" / "recordings"


def rms_to_db(rms: float) -> float:
    """Convert RMS amplitude to dB."""
    if rms < 1e-10:
        return -100.0
    return 20.0 * np.log10(rms)


def detect_silence(wav_path: Path, threshold_db: float = SILENCE_THRESHOLD_DB) -> bool:
    """Return True if the last SILENCE_DURATION seconds of audio are below threshold."""
    with wave.open(str(wav_path), "rb") as wf:
        total_frames = wf.getnframes()
        silence_frames = int(SILENCE_DURATION * SAMPLE_RATE)
        if total_frames < silence_frames:
            return False
        wf.setpos(total_frames - silence_frames)
        raw = wf.readframes(silence_frames)

    audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    rms = float(np.sqrt(np.mean(audio ** 2)))
    db = rms_to_db(rms)
    return db < threshold_db


def record(output_path: Path, max_seconds: int = 30) -> Path:
    """
    Record audio via arecord until silence or max_seconds.

    Returns the path to the saved WAV file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "arecord",
        "-f", "S16_LE",
        "-r", str(SAMPLE_RATE),
        "-c", str(CHANNELS),
        "-d", str(max_seconds),  # hard upper limit
        str(output_path),
    ]

    print("Listening... (Ctrl+C to stop early)", flush=True)
    start_time = time.time()

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    def _stop(sig, frame):
        proc.terminate()

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)

    try:
        # Poll for silence while arecord runs
        while proc.poll() is None:
            elapsed = time.time() - start_time
            if elapsed > max_seconds:
                proc.terminate()
                break

            # Wait for a chunk of audio to accumulate before checking
            if elapsed > SILENCE_DURATION + 1.0 and output_path.exists():
                if detect_silence(output_path, SILENCE_THRESHOLD_DB):
                    print("(silence detected — stopping)", flush=True)
                    proc.terminate()
                    break

            time.sleep(0.2)

        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        proc.wait()

    # Restore default signal handlers
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)

    if not output_path.exists() or output_path.stat().st_size == 0:
        print("ERROR: No audio was recorded.", file=sys.stderr)
        sys.exit(1)

    elapsed = time.time() - start_time
    print(f"Recorded {elapsed:.1f}s -> {output_path}", flush=True)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Push-to-talk recorder for Jarvis")
    parser.add_argument(
        "--max-seconds",
        type=int,
        default=30,
        help="Maximum recording duration in seconds (default: 30)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output WAV path (default: data/voice/recordings/in-{timestamp}.wav)",
    )
    args = parser.parse_args()

    if args.output:
        output_path = Path(args.output)
    else:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = RECORDINGS_DIR / f"in-{ts}.wav"

    saved = record(output_path, max_seconds=args.max_seconds)
    print(saved)


if __name__ == "__main__":
    main()
