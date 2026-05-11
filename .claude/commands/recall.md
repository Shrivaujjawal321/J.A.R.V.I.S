# /recall — Semantic Memory Recall

Search Jarvis's episodic memory for anything stored from past conversations,
memory files, notes, briefings, or research outputs.

## Usage
```
/recall <natural language question>
```

**Examples:**
- `/recall what did we discuss about my resume`
- `/recall Anisha birthday`
- `/recall hackathon deadlines`
- `/recall Hinglish preference`
- `/recall what are Boss's peak focus hours`

## What Happens

1. Run recall CLI against the vector DB:
   ```bash
   .venv/bin/python scripts/recall_cli.py "$ARGUMENTS" --k 8
   ```

2. Display the top results (source file + section + relevance score + 300-char snippet).

3. Ask: **"Want me to use this context for your next message? (yes/no)"**

## Notes

- If results are empty, the DB may need seeding — run bootstrap:
  ```bash
  .venv/bin/python scripts/bootstrap_memory.py
  ```
- Score shown as `0–100%`. Results above 70% are highly relevant;
  40–70% is fuzzy/associative; below 40% may be noise.
- Source paths tell you *where* the info came from
  (`data/memory/preferences.md`, `data/notes/resume-research-*.md`, etc.)
- The DB is re-indexed nightly at 04:00 IST by the systemd timer
  `jarvis-memory-ingest.timer`. To manually re-ingest a changed file:
  ```bash
  .venv/bin/python scripts/incremental_memory_ingest.py
  ```

## Filter by source (advanced)

To search only within a specific file type, use the Python API directly:
```python
from scripts.episodic_memory import EpisodicMemory
mem = EpisodicMemory()
results = mem.recall("resume research", k=5, filter={"source": {"$contains": "notes"}})
```
