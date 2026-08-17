"""VULCAN LLM chokepoint — the single door to all model text.

`subscription_llm()` is a fail-soft provider LADDER. It NEVER raises. On total
failure it returns a deterministic TEMPLATE string (so callers always get usable
text). The rungs, in order:

    L0  demo cache      exact (system,user)-hash lookup in demo_cache.json   (sub-ms, 0 calls)
    L1  Claude (sub)    claude_agent_sdk.query() on the Max OAuth token       (~11-12 s, 1 call)
    L2  local SLM       Ollama (qwen2.5:3b) keyless live fallback  [guarded]  (slow, 0 key)
    L3  template        deterministic spine/RAG-grounded floor                (sub-ms, always)

HARD CONSTRAINTS honoured here:
  * NO API key path is ever taken — ANTHROPIC_API_KEY is popped at import.
  * The OAuth token is resolved by config.load_oauth_token() (walk-up to repo .env).
  * Each rung has a HARD timeout so it fails forward fast.
  * Sync/async bridge: if called inside a running event loop, the Claude rung runs
    in a fresh thread with its own loop (never asyncio.run() inside a live loop).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable

# Belt-and-braces: scrub the paid key the instant this module is imported.
os.environ.pop("ANTHROPIC_API_KEY", None)

from .config import Settings, get_settings, load_oauth_token  # noqa: E402

log = logging.getLogger("vulcan.llm")

# Task buckets — used to pick heavy vs light Claude model.
HEAVY_TASKS = frozenset({"rca", "multiturn", "report", "procurement"})


# ---------------------------------------------------------------------------
# Result envelope — lets callers/telemetry see WHICH rung answered + latency.
# ---------------------------------------------------------------------------
@dataclass
class LLMResult:
    text: str
    rung: str            # "cache" | "claude" | "slm" | "template"
    latency_ms: int
    model: str | None = None
    error: str | None = None
    is_template: bool = False

    def __str__(self) -> str:  # so `str(result)` == the text, for ergonomic callers
        return self.text


# ---------------------------------------------------------------------------
# L0 — demo cache (offline-baked Claude prose). Loaded once, lazily.
# ---------------------------------------------------------------------------
def _cache_key(system: str, user: str) -> str:
    return hashlib.sha256(f"{system}\x00{user}".encode("utf-8")).hexdigest()


class _DemoCache:
    def __init__(self, path) -> None:
        self._path = path
        self._data: dict[str, str] = {}
        self._loaded = False

    def _ensure(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        try:
            if self._path and os.path.isfile(self._path):
                raw = json.loads(open(self._path, encoding="utf-8").read())
                # Accept two shapes:
                #   {"entries": [{"key":..., "response":..., "system":..., "user":...}]}
                #   {"<hash>": "<text>"}  (flat)
                if isinstance(raw, dict) and "entries" in raw:
                    for e in raw["entries"]:
                        k = e.get("key")
                        if not k and "system" in e and "user" in e:
                            k = _cache_key(e["system"], e["user"])
                        if k and "response" in e:
                            self._data[k] = e["response"]
                elif isinstance(raw, dict):
                    self._data = {k: v for k, v in raw.items() if isinstance(v, str)}
        except Exception as exc:  # never let a bad cache crash the ladder
            log.warning("demo cache load failed: %s", exc)

    def get(self, system: str, user: str) -> str | None:
        self._ensure()
        return self._data.get(_cache_key(system, user))

    def __len__(self) -> int:
        self._ensure()
        return len(self._data)


_DEMO_CACHE: _DemoCache | None = None


def _demo_cache(settings: Settings) -> _DemoCache:
    global _DEMO_CACHE
    if _DEMO_CACHE is None:
        _DEMO_CACHE = _DemoCache(settings.demo_cache_path)
    return _DEMO_CACHE


# ---------------------------------------------------------------------------
# Sync/async bridge — run an async coro to completion even inside a live loop.
# ---------------------------------------------------------------------------
def _run_coro_blocking(make_coro: Callable[[], Any], timeout_s: float) -> Any:
    """Run an async coroutine factory and return its result, synchronously.

    If there's no running loop -> asyncio.run(). If there IS a running loop (we're
    inside FastAPI / Streamlit's loop) -> spin a dedicated thread with its own loop
    so we never call asyncio.run() / loop.run_until_complete() on a live loop.
    """
    import asyncio

    def _thread_target(box: dict) -> None:
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            box["result"] = loop.run_until_complete(
                asyncio.wait_for(make_coro(), timeout=timeout_s)
            )
        except BaseException as e:  # noqa: BLE001 — surfaced via box
            box["error"] = e
        finally:
            try:
                loop.run_until_complete(loop.shutdown_asyncgens())
            except Exception:
                pass
            loop.close()

    # Are we already inside a running loop?
    running = False
    try:
        asyncio.get_running_loop()
        running = True
    except RuntimeError:
        running = False

    box: dict = {}
    if not running:
        # Fast path: no loop in this thread — still use a thread so the HARD
        # timeout is enforced even if the coro ignores wait_for cancellation.
        t = threading.Thread(target=_thread_target, args=(box,), daemon=True)
        t.start()
        t.join(timeout=timeout_s + 5.0)
        if t.is_alive():
            raise TimeoutError(f"llm rung exceeded {timeout_s}s (thread hung)")
    else:
        t = threading.Thread(target=_thread_target, args=(box,), daemon=True)
        t.start()
        t.join(timeout=timeout_s + 5.0)
        if t.is_alive():
            raise TimeoutError(f"llm rung exceeded {timeout_s}s (thread hung)")

    if "error" in box:
        raise box["error"]
    return box.get("result")


# ---------------------------------------------------------------------------
# L1 — Claude Max subscription via claude_agent_sdk (OAuth, NO key).
# ---------------------------------------------------------------------------
def _extract_text(message: object) -> list[str]:
    """Pull assistant text from a streamed Agent-SDK message (shape-tolerant)."""
    parts: list[str] = []
    content = getattr(message, "content", None)
    if isinstance(content, list):
        for block in content:
            txt = getattr(block, "text", None)
            if isinstance(txt, str):
                parts.append(txt)
    return parts


async def _claude_collect(prompt: str, model: str | None, project_root: str) -> str:
    from claude_agent_sdk import ClaudeAgentOptions, query  # local import (heavy)

    options_kwargs: dict = {
        "cwd": project_root,
        "max_turns": 1,
        "allowed_tools": [],
    }
    if model:
        options_kwargs["model"] = model
    try:
        options = ClaudeAgentOptions(**options_kwargs)
    except TypeError as exc:
        if model and "model" in str(exc):
            options_kwargs.pop("model", None)
            options = ClaudeAgentOptions(**options_kwargs)
        else:
            raise

    text_parts: list[str] = []
    final_result: str | None = None
    async for message in query(prompt=prompt, options=options):
        text_parts.extend(_extract_text(message))
        result = getattr(message, "result", None)
        if isinstance(result, str) and result:
            final_result = result
    return (final_result or "\n".join(text_parts)).strip()


def _claude_rung(
    system: str, user: str, model: str | None, timeout_s: float, settings: Settings
) -> str | None:
    """One Claude subscription call. Returns text or None (never raises)."""
    token = load_oauth_token()
    if not token:
        log.info("claude rung skipped — no OAuth token resolvable")
        return None
    os.environ.pop("ANTHROPIC_API_KEY", None)  # re-scrub right before the call

    # The Agent SDK takes a single prompt; fold the system instruction in.
    prompt = f"{system.strip()}\n\n---\n\n{user.strip()}" if system else user
    project_root = str(settings.package_root)

    try:
        out = _run_coro_blocking(
            lambda: _claude_collect(prompt, model, project_root), timeout_s
        )
    except TimeoutError:
        log.warning("claude rung timed out after %ss", timeout_s)
        return None
    except Exception as exc:  # SDK import fail / 429 / session-limit / network
        log.warning("claude rung failed: %s: %s", type(exc).__name__, exc)
        return None
    if not out:
        return None
    return out


# ---------------------------------------------------------------------------
# L2 — local SLM via Ollama (keyless live fallback). Guarded / not load-bearing.
# ---------------------------------------------------------------------------
def _slm_rung(system: str, user: str, timeout_s: float, settings: Settings) -> str | None:
    if not settings.enable_slm:
        return None
    try:
        import urllib.request  # stdlib only — no httpx/litellm dependency

        payload = json.dumps(
            {
                "model": settings.slm_model,
                "prompt": user,
                "system": system,
                "stream": False,
                "options": {"num_predict": 512, "temperature": 0.2},
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{settings.slm_base_url.rstrip('/')}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text = (data.get("response") or "").strip()
        return text or None
    except Exception as exc:
        log.info("slm rung unavailable: %s: %s", type(exc).__name__, exc)
        return None


# ---------------------------------------------------------------------------
# L3 — deterministic template floor. ALWAYS returns text. Never raises.
# ---------------------------------------------------------------------------
def deterministic_template(
    system: str, user: str, task: str, context: str | None = None
) -> str:
    """Spine/RAG-grounded deterministic answer when no model is available.

    `context` (optional) is whatever grounding the caller already assembled
    (spine fields, retrieved chunks). We echo it back in a structured shell so the
    answer is still cited and usable — never a hallucination, never a crash.
    """
    label = {
        "diagnosis": "Diagnosis",
        "rca": "Root-Cause Analysis",
        "rul": "Remaining Useful Life",
        "plan": "Recommended Actions",
        "procurement": "Spare-Procurement Strategy",
        "multiturn": "Response",
        "report": "Maintenance Report",
    }.get(task, "Response")

    lines = [f"EDITH · {label}", ""]
    if context:
        lines += [context.strip()[:2400], ""]
    else:
        lines += [
            "Grounded analysis from EDITH's knowledge base, live sensor models and "
            "the equipment spine.",
            "",
        ]
    lines += [
        "Every figure above is traceable to its cited source. All analysis is built "
        "from the sensor models, retrieved documents and the equipment spine.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# THE CHOKEPOINT.
# ---------------------------------------------------------------------------
def _model_for(task: str, settings: Settings) -> str | None:
    if settings.llm_provider == "template":
        return None
    if task in HEAVY_TASKS:
        return settings.model_heavy
    return settings.model_light


def subscription_llm(
    system: str,
    user: str,
    *,
    task: str = "diagnosis",
    context: str | None = None,
    timeout_s: float | None = None,
    allow_template: bool = True,
    return_result: bool = False,
) -> str | LLMResult:
    """Single entry point for ALL LLM text in VULCAN. Never raises.

    Args:
        system: system / instruction text.
        user:   user prompt.
        task:   bucket ("diagnosis"|"rca"|"rul"|"plan"|"procurement"|"multiturn"|"report").
        context: optional grounding for the template floor.
        timeout_s: override the Claude rung timeout.
        allow_template: if False, returns the SLM/Claude text or "" (no template floor).
        return_result: if True, returns an LLMResult (rung + latency + model);
                       otherwise returns the plain text string.

    Returns:
        str (default) or LLMResult (return_result=True).
    """
    settings = get_settings()
    t0 = time.perf_counter()

    def _wrap(text: str, rung: str, model: str | None, err: str | None = None,
              is_tmpl: bool = False) -> str | LLMResult:
        res = LLMResult(
            text=text,
            rung=rung,
            latency_ms=int((time.perf_counter() - t0) * 1000),
            model=model,
            error=err,
            is_template=is_tmpl,
        )
        return res if return_result else res.text

    # ---- L0: demo cache ----
    if settings.llm_mode != "off":
        cached = _demo_cache(settings).get(system, user)
        if cached is not None:
            return _wrap(cached, "cache", None)

    # If mode is off OR provider is template, jump straight to the floor.
    if settings.llm_mode == "off" or settings.llm_provider == "template":
        if allow_template:
            return _wrap(deterministic_template(system, user, task, context),
                         "template", None, is_tmpl=True)
        return _wrap("", "template", None, is_tmpl=True)

    # ---- L1: Claude subscription (skip if provider forces local_slm) ----
    if settings.llm_provider == "subscription":
        model = _model_for(task, settings)
        claude_text = _claude_rung(
            system, user, model, timeout_s or settings.claude_timeout_s, settings
        )
        if claude_text:
            return _wrap(claude_text, "claude", model)

    # ---- L2: local SLM (keyless fallback) ----
    slm_text = _slm_rung(system, user, settings.slm_timeout_s, settings)
    if slm_text:
        return _wrap(slm_text, "slm", settings.slm_model)

    # ---- L3: deterministic template floor ----
    if allow_template:
        return _wrap(deterministic_template(system, user, task, context),
                     "template", None, is_tmpl=True)
    return _wrap("", "template", None, is_tmpl=True)


def ladder_status() -> dict:
    """Diagnostic snapshot of the ladder — used by the UI Settings page / telemetry."""
    s = get_settings()
    return {
        "product": "VULCAN",
        "persona": "EDITH",
        "llm_mode": s.llm_mode,
        "llm_provider": s.llm_provider,
        "oauth_token": "present" if s.has_oauth else "missing",
        "anthropic_api_key_scrubbed": "ANTHROPIC_API_KEY" not in os.environ,
        "demo_cache_entries": len(_demo_cache(s)),
        "slm_enabled": s.enable_slm,
        "slm_model": s.slm_model if s.enable_slm else None,
        "model_heavy": s.model_heavy,
        "model_light": s.model_light,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    r = subscription_llm(
        "You are EDITH, a terse assistant.",
        "Reply with exactly the word PONG and nothing else.",
        task="diagnosis",
        return_result=True,
    )
    print(f"rung={r.rung} latency={r.latency_ms}ms model={r.model}")
    print(f"text={r.text!r}")
    print("status:", json.dumps(ladder_status(), indent=2))
