# Architecture Roadmap — Ratnesh-Jarvis Ports

**Status:** active
**Owner:** roadmap (no code)
**Last reviewed:** 2026-05-15

## Context

On 2026-05-15 Boss asked Jarvis to compare itself with Ratnesh's Jarvis (`Jarvis-master/` on the same machine — Windows-based, Electron-app-driven). Deep-read of CLAUDE.md, MEMORY.md, identity/, knowledge/, blueprint. Five architectural patterns from that system were identified as worth porting:

| Pattern | Value | Effort | Risk | Decision |
|---------|-------|--------|------|----------|
| Mandatory intent classifier | High — every turn benefits | Medium | Low | **SHIPPED 2026-05-15** |
| Memory zone/type frontmatter | Medium — foundation for lifecycle | Low | Low | **SHIPPED 2026-05-15** |
| Memory lifecycle engine | High — auto-promotion/demotion | High | Medium | **ROADMAP — this doc** |
| Persistent sentinels | High — anticipation built-in | High | Medium | **ROADMAP — this doc** |
| Event bus (pub/sub) | Medium — architectural shift | Very High | High | **ROADMAP — this doc** |
| Web dashboard | High long-term | Very High | Low | **ROADMAP — this doc** |

This document specifies the four pending roadmap items. Each section is self-contained: a clear problem statement, the design at a level a future session could implement from cold, dependencies, and a 1-line definition of done.

---

## R1. Memory Lifecycle Engine

### Problem
Today `data/memory/*.md` files accumulate. There is no decay, no auto-promotion, no audit. A 6-month-old `projects.md` entry about a killed project sits alongside a critical active-project entry with equal weight. The recall layer treats both the same.

### Design
**Three-zone model (already tagged in frontmatter):**
- `hot` — current session, ephemeral
- `warm` — recent learnings, auto-expire after N days unless accessed
- `cold` — proven knowledge, permanent until invalidated

**Four memory types (already tagged):**
- `fact` — decay fast, must reverify
- `principle` — decay slow, high value
- `skill` — periodic test
- `model` — incremental update, never bulk-replace

**Engine responsibilities:**
1. Read each `data/memory/*.md` frontmatter on startup → build in-memory index of (path, type, zone, last_reviewed, access_count).
2. Track access count via hook into `recall.py` — every memory hit increments the source file's counter.
3. Daily cron at 04:00 IST (`jarvis-memory-lifecycle.timer`):
   - Warm → Cold: accessed ≥3 times AND age > 14 days AND not a `fact` type (facts must be re-verified, not auto-promoted).
   - Warm → Deleted (archived): not accessed in 30 days AND no manual `pin: true` flag.
   - Cold audit: type=`fact` entries older than `last_reviewed + 90 days` → flag to `data/memory/_review_queue.md` for Boss.
4. Emit lifecycle events to a new `data/logs/memory_lifecycle.jsonl`.
5. Archive deletions move file/section to `data/memory/_archive/YYYY-MM/` — never hard-delete.

### Implementation
- `jarvis_core/memory_lifecycle.py` — engine
- `specs/memory-lifecycle.spec.md` — contract
- `scripts/memory_lifecycle.py` — cron entry point
- Systemd: `jarvis-memory-lifecycle.service` + `.timer` (daily 04:00 IST)
- Integration: `recall.py` increments access counter on every recalled chunk

### Definition of done
A `projects.md` entry tagged `zone: warm` that hasn't been recalled in 30 days gets archived to `_archive/2026-06/projects.md` and removed from the live ChromaDB index. `_review_queue.md` lists every `fact` older than 90 days.

### Dependencies
- Memory frontmatter ([SHIPPED 2026-05-15])
- ChromaDB incremental re-index hook (already in `scripts/incremental_memory_ingest.py`)

---

## R2. Persistent Sentinels

### Problem
Today's "always-on" work is periodic timers:
- `auto_capture` every 30 min
- `reasoning_trigger` every 4 hr
- `self_growth_weekly` every Sunday
These are **polling**, not event-driven. Ratnesh's sentinels are subscribed to specific event types and react in milliseconds.

Concrete miss: when a `data/logs/critic.jsonl` line records a `verdict: low` reply, nothing reacts. A sentinel could flag it within seconds.

### Design
**Five sentinels (subset of Ratnesh's 8 — drop the ones I don't need):**

| Sentinel | Subscribes to | Action |
|----------|--------------|--------|
| Watcher | All inbound (Telegram msg arrival, voice trigger, cron fire) | Update a `live_state.json` Boss can poke |
| Auditor | `memory.write`, `intent.error`, `critic.error`, agent timeout | Append to `data/logs/audit.jsonl`; weekly digest |
| Strategist | `digest.daily` | Look 7-30 days ahead — surface decisions before they're forced |
| Analyst | `goal.completed`, `task.completed` | Per-project rollup: velocity, cost, blockers |
| Bridge | Telegram-bridge restart, daemon restart, voice loop restart | Consistency check on state.json + live sessions |

**Skip Ratnesh's:** Learner (I use research-agent on-demand), Scribe (I have JSONL logs), Trainer (I have eval framework).

### Implementation
Each sentinel = an `asyncio.Task` spawned in `daemon.py` `lifespan()`. Subscribes via an in-process pub/sub built on `asyncio.Queue`. No external broker — keep it lean.

- `jarvis_core/sentinels/__init__.py` — registry
- `jarvis_core/sentinels/base.py` — abstract `Sentinel` class
- `jarvis_core/sentinels/{watcher,auditor,strategist,analyst,bridge}.py`
- `jarvis_core/event_bus.py` — minimal in-process pub/sub (precursor to full R3)
- `specs/sentinels.spec.md` — contract per sentinel

### Definition of done
A `verdict: low` critique line emitted at 02:00 IST results in an `data/logs/audit.jsonl` entry within 5 seconds, surfaced in the morning digest.

### Dependencies
- Event bus (R3) — but a stub in-process Queue suffices for v1
- ChatResponse intent/priority (SHIPPED 2026-05-15) — Watcher uses these

### Risk note
Five new always-on tasks inside `daemon.py` increase memory footprint by ~50MB and add restart-risk. Keep each sentinel sleep-default-on-empty-queue.

---

## R3. Event Bus

### Problem
Components today couple directly: `daemon.py` calls `recall` → `worker` → `critic` in sequence. `auto_capture` reads a JSONL file written by daemon. `self_growth_weekly` reads several JSONL files. **Fan-out is hard.** Adding a 6th consumer of "Boss sent a message" means another file-tail or import.

### Design
Single pub/sub bus with typed events. SQLite-persisted ring buffer (last 5000 events) + in-memory subscribers.

**Event schema:**
```python
class Event(BaseModel):
    event_id: str       # uuid4
    type: str           # dot-namespaced: "chat.received", "intent.classified", ...
    source: str         # component name
    timestamp: datetime
    priority: int       # 0..3 (low → urgent)
    payload: dict[str, Any]
```

**Topics (initial):**
- `chat.received`, `chat.replied`
- `intent.classified`
- `memory.recalled`, `memory.written`, `memory.lifecycle.*`
- `worker.spawned`, `worker.completed`, `worker.error`
- `critic.evaluated`, `critic.low_confidence`
- `goal.queued`, `goal.completed`, `goal.failed`, `approval.requested`, `approval.decided`
- `telegram.message`, `voice.transcribed`

**Publisher API:**
```python
await bus.publish(Event(type="intent.classified", source="daemon", payload={...}))
```

**Subscriber API:**
```python
@bus.subscribe("intent.classified")
async def on_intent(event: Event): ...
```

### Implementation
- `jarvis_core/event_bus.py` — singleton, lifecycle-managed by daemon
- SQLite backing at `data/state/events.db`
- MCP tool `events_query` for ad-hoc inspection
- `specs/event-bus.spec.md` — contract

### Definition of done
Replace the existing `_append_conversation_log` call in `daemon.py` with `bus.publish(Event(type="chat.replied", ...))` and have `auto_capture` consume via subscribe instead of file-tail. Behaviour identical, fan-out free.

### Dependencies
- None — but R2 (Sentinels) should land first as the first heavy consumer.

### Risk note
This is the biggest port. ~3 days of work. Defer until after R1 + R2 prove the architectural pull.

---

## R4. Web Dashboard

### Problem
Today Jarvis is invisible. To see what's running you tail logs, query daemon `/state`, or open Telegram. There's no glanceable health view.

Ratnesh's CC Doctrine: **"no capability without visibility, no visibility without control."** Today I violate this.

### Design
Lightweight Next.js 15 dashboard on `http://localhost:8765/dashboard` (served by daemon, no separate process). Read-only initially; action buttons in v2.

**Panels:**
1. **Live state** — last 10 intents (category + priority), last 5 worker spawns, current goal queue
2. **Agents** — live worker list with cost / tokens / duration
3. **Memory** — ChromaDB chunk count, memory-zone heatmap, files with type/zone/last_reviewed
4. **Goals** — queue with status, approval queue, recent completions
5. **Health** — daemon uptime, recent errors, latency p50/p95
6. **Logs** — streaming JSONL view, filterable

### Implementation
- `dashboard/` — Next.js App Router, RSC, Tailwind 4, shadcn/ui v4
- API: extend daemon `/state`, add `/events/stream` SSE endpoint
- Real-time via SSE (not WebSocket — simpler)
- `specs/web-dashboard.spec.md` — contract

### Definition of done
Open `localhost:8765/dashboard`, see live intent categories streaming in as Boss messages arrive on Telegram, with no manual refresh.

### Dependencies
- Event bus (R3) for the SSE stream
- All other R-items can be shipped without dashboard but dashboard pays back ×3 once it lands

### Risk note
Frontend is the biggest time-sink ratio (3-5 days). Defer until R1-R3 are stable.

---

## Sequencing

```
SHIPPED                R1 (lifecycle)       R2 (sentinels)       R3 (event bus)       R4 (dashboard)
────────               ───────────────      ──────────────       ──────────────       ────────────────
intent classifier  →   2-3 days (next)  →   3-4 days        →    3-4 days       →    4-5 days
memory frontmatter
                       depends on:          depends on:          depends on:          depends on:
                       frontmatter          stub Queue           nothing              event bus
                       (DONE)               (use stub first)
```

Total estimate to full Ratnesh-parity: **12-16 active days** spread across calendar weeks, gated on Boss's other priorities (resume, hackathon, RAG Decathlon).

## Anti-goals

We are **not** porting:
- Ratnesh's Electron Control Centre (we're CLI/Telegram/web — different UX surface)
- WhatsApp Baileys integration (Telegram is the channel)
- The "Jarvis cannot edit code" doctrine — I'm a builder, not just an orchestrator
- 278 custom MCP tools — Composio's catalog plus targeted custom modules is leaner

## Changelog

- 2026-05-15: Initial draft. Intent classifier + memory frontmatter shipped in same commit.
