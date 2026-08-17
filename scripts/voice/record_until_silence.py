#!/usr/bin/env python3
"""Record from mic until the speaker goes silent — real-interview style.

Streams raw audio from `arecord`, watches RMS energy:
- calibrates ambient noise for the first second
- starts "speech" once energy crosses threshold
- stops after SILENCE_STOP seconds of continuous quiet (post-speech)
- hard caps at MAX_SEC; aborts if no speech within NO_SPEECH_TIMEOUT

Usage:
    record_until_silence.py --output out.wav [--max 180] [--silence 3.0]
"""
import argparse
import subprocess
import sys
import wave

import numpy as np

RATE = 16000
CHUNK_SEC = 0.25
CHUNK_SAMPLES = int(RATE * CHUNK_SEC)
CHUNK_BYTES = CHUNK_SAMPLES * 2  # S16_LE mono


def rms(chunk: bytes) -> float:
    a = np.frombuffer(chunk, dtype=np.int16).astype(np.float64)
    if a.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(a * a)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--max", type=float, default=180.0, help="hard cap seconds")
    ap.add_argument("--silence", type=float, default=3.0,
                    help="stop after this many seconds of quiet once speech began")
    ap.add_argument("--no-speech-timeout", type=float, default=20.0,
                    help="abort if speech never starts within this window")
    args = ap.parse_args()

    proc = subprocess.Popen(
        ["arecord", "-q", "-f", "S16_LE", "-r", str(RATE), "-c", "1", "-t", "raw", "-"],
        stdout=subprocess.PIPE,
    )

    frames: list[bytes] = []
    ambient: list[float] = []
    threshold = None
    speech_started = False
    quiet_run = 0.0
    elapsed = 0.0

    try:
        while elapsed < args.max:
            chunk = proc.stdout.read(CHUNK_BYTES)
            if not chunk:
                break
            frames.append(chunk)
            elapsed += CHUNK_SEC
            level = rms(chunk)

            if threshold is None:
                if elapsed <= 0.5:
                    continue  # discard first 0.5s (beep echo / speaker bleed)
                ambient.append(level)
                if elapsed >= 1.0:  # calibrate on the next 0.5s
                    base = max(min(ambient), 1.0)  # quietest chunk = true floor
                    threshold = min(max(300.0, base * 1.6), 1500.0)  # cap: speech ~1200-2700
                    print(f"calibrated threshold={threshold:.0f}", file=sys.stderr)
                continue

            if level > threshold:
                if not speech_started:
                    print("speech detected", file=sys.stderr)
                speech_started = True
                quiet_run = 0.0
            else:
                quiet_run += CHUNK_SEC
                if speech_started and quiet_run >= args.silence:
                    print(f"silence {args.silence}s -> stop", file=sys.stderr)
                    break
                if not speech_started and elapsed >= args.no_speech_timeout:
                    print("no speech detected, aborting", file=sys.stderr)
                    break
    finally:
        proc.terminate()
        proc.wait()

    with wave.open(args.output, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(frames))

    dur = len(frames) * CHUNK_SEC
    print(f"saved {args.output} ({dur:.1f}s, spoke={speech_started})")
    return 0 if speech_started else 1


if __name__ == "__main__":
    sys.exit(main())
