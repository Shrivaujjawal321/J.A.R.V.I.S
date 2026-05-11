# /voice — Jarvis Voice Interface

Manage and use the Jarvis voice interface (STT + TTS pipeline).

## Usage

```
/voice         — show pipeline status
/voice on      — start interactive voice loop (foreground)
/voice off     — kill running voice loop
/voice test    — smoke test: record 5s, transcribe, speak back
/voice mute    — suppress TTS output (sets dev_mode_active marker)
/voice unmute  — restore TTS output
```

---

## Subcommand Details

### `/voice` (status)

Check health of the full pipeline:

```bash
VENV=/home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python
ROOT=/home/ujjwal/Documents/J.A.R.V.I.S.

# 1. Package checks
$VENV -c "import whisper; print('Whisper OK')" 2>/dev/null || echo "Whisper MISSING"
$VENV -c "from piper import PiperVoice; print('Piper OK')" 2>/dev/null || echo "Piper MISSING"

# 2. System tools
which arecord aplay gst-launch-1.0

# 3. Voice model
ls -lh $ROOT/data/voice/models/

# 4. Whisper model cache
ls -lh ~/.cache/whisper/ 2>/dev/null || echo "No whisper cache"

# 5. Last recording
ls -lt $ROOT/data/voice/recordings/ | head -3

# 6. Dev mode
test -f $ROOT/data/markers/dev_mode_active && echo "DEV MODE: voice muted" || echo "Voice: active"
```

Report: installed packages, model sizes, last recording timestamp, dev_mode status.

---

### `/voice on`

Start the voice loop in a foreground subprocess.

```bash
ROOT=/home/ujjwal/Documents/J.A.R.V.I.S.
$ROOT/.venv/bin/python $ROOT/scripts/voice/voice_loop.py
```

- Boss presses Enter to speak each turn
- Ctrl+C or 'q' to exit
- Logs every turn to `data/voice/transcripts/{date}.jsonl`

---

### `/voice off`

Kill any running voice_loop.py:

```bash
pkill -f "voice_loop.py" && echo "Voice loop stopped" || echo "No voice loop running"
```

---

### `/voice test`

Full pipeline smoke test:

1. Generate a TTS WAV:
```bash
ROOT=/home/ujjwal/Documents/J.A.R.V.I.S.
$ROOT/.venv/bin/python $ROOT/scripts/voice/speak.py \
  --text "Jarvis voice test. Say something after the beep." \
  --output $ROOT/data/voice/test/smoke_tts.wav
echo "TTS done: $?"
```

2. Play it:
```bash
aplay $ROOT/data/voice/test/smoke_tts.wav
```

3. Record 5 seconds:
```bash
arecord -f S16_LE -r 16000 -c 1 -d 5 $ROOT/data/voice/test/smoke_record.wav
```

4. Transcribe:
```bash
$ROOT/.venv/bin/python $ROOT/scripts/voice/transcribe.py \
  --input $ROOT/data/voice/test/smoke_record.wav
```

5. Speak transcription back:
```bash
TEXT=$($ROOT/.venv/bin/python $ROOT/scripts/voice/transcribe.py \
  --input $ROOT/data/voice/test/smoke_record.wav)
$ROOT/.venv/bin/python $ROOT/scripts/voice/speak.py --text "$TEXT"
```

Report the transcript and whether audio played correctly.

---

### `/voice mute`

```bash
touch /home/ujjwal/Documents/J.A.R.V.I.S./data/markers/dev_mode_active
echo "Voice muted. voice_loop.py will suppress TTS."
```

### `/voice unmute`

```bash
rm -f /home/ujjwal/Documents/J.A.R.V.I.S./data/markers/dev_mode_active
echo "Voice restored."
```

---

## Privacy Notes

- Recordings saved to: `data/voice/recordings/` (WAV files)
- Transcripts saved to: `data/voice/transcripts/{date}.jsonl`
- To purge: `rm data/voice/recordings/*.wav data/voice/transcripts/*.jsonl`
- Telegram voice OGGs also saved to `data/voice/recordings/tg-{ts}.ogg`

## Known Limitations

- Hinglish: Whisper `base` handles it at ~70-80% accuracy. Hindi-heavy speech may
  be less accurate. Use `--model small` in transcribe.py for better accuracy.
- Piper pronounces Hindi words with English phonetics (known limitation).
- PortAudio not installed — sounddevice doesn't work. Using arecord/aplay (ALSA).
- ffmpeg not installed — Whisper uses scipy WAV loading directly (no ffmpeg needed).
