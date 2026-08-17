"""VULCAN configuration — paths, LLM mode, and repo-root .env resolution.

No API key anywhere. The Claude Max OAuth token (`CLAUDE_CODE_OAUTH_TOKEN`) is
resolved by a *walk-up* loader that climbs parent directories until it finds the
repo-root `.env` (the exact pattern proven in `jarvis_core` and the EDITH agent).

`ANTHROPIC_API_KEY` is popped at import time everywhere LLM code runs so the SDK
can never accidentally take the paid-key path.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Literal

# ---------------------------------------------------------------------------
# Key scrub — belt-and-braces: pop any stray paid key the moment config loads.
# ---------------------------------------------------------------------------
os.environ.pop("ANTHROPIC_API_KEY", None)

# ---------------------------------------------------------------------------
# .env walk-up loader (NO python-dotenv dependency — hand-parsed, robust).
# ---------------------------------------------------------------------------
_OAUTH_KEYS = ("CLAUDE_CODE_OAUTH_TOKEN", "CLAUDE_OAUTH_TOKEN")


def _parse_env_file(path: Path) -> dict[str, str]:
    """Parse a .env file into a dict. Tolerates `export `, quotes, comments."""
    out: dict[str, str] = {}
    try:
        for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.lower().startswith("export "):
                line = line[len("export "):].lstrip()
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key:
                out[key] = val
    except OSError:
        pass
    return out


def find_repo_root_env(start: Path | None = None, max_up: int = 12) -> Path | None:
    """Walk up from `start` (default: this file) looking for the repo-root .env.

    The repo-root .env is the one that holds CLAUDE_CODE_OAUTH_TOKEN. We accept
    the first .env that contains an OAuth key; otherwise the topmost .env found.
    """
    here = (start or Path(__file__).resolve()).resolve()
    fallback: Path | None = None
    for parent in [here, *here.parents][:max_up + 1]:
        candidate = parent / ".env"
        if candidate.is_file():
            if fallback is None:
                fallback = candidate
            parsed = _parse_env_file(candidate)
            if any(k in parsed for k in _OAUTH_KEYS):
                return candidate
    return fallback


def load_oauth_token() -> str | None:
    """Return the Claude Max OAuth token. Env var wins; else walk-up to repo .env.

    Side effect: ensures the token is exported into os.environ (so the Agent SDK
    subprocess inherits it) and re-scrubs ANTHROPIC_API_KEY.
    """
    os.environ.pop("ANTHROPIC_API_KEY", None)
    for k in _OAUTH_KEYS:
        v = os.getenv(k)
        if v:
            os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = v
            return v
    env_path = find_repo_root_env()
    if env_path:
        parsed = _parse_env_file(env_path)
        for k in _OAUTH_KEYS:
            if parsed.get(k):
                os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = parsed[k]
                # also hydrate the rest of repo .env values that aren't already set,
                # but never re-introduce a paid key
                for ek, ev in parsed.items():
                    if ek == "ANTHROPIC_API_KEY":
                        continue
                    os.environ.setdefault(ek, ev)
                os.environ.pop("ANTHROPIC_API_KEY", None)
                return parsed[k]
    return None


# ---------------------------------------------------------------------------
# Dataset path resolution — the flagship dataset, relative to round_2/.
# ---------------------------------------------------------------------------
def _default_dataset_root() -> Path:
    """Best-effort locate of steel-maintenance-flagship.

    Honours $VULCAN_DATASET_ROOT, else walks up to find round_2/dataforge/...
    """
    env = os.getenv("VULCAN_DATASET_ROOT")
    if env and Path(env).is_dir():
        return Path(env).resolve()
    here = Path(__file__).resolve()
    rel = Path("dataforge/datasets/steel-maintenance-flagship")
    for parent in here.parents:
        candidate = parent / rel
        if candidate.is_dir():
            return candidate.resolve()
        # also handle being inside round_2 already
        if parent.name == "round_2" and (parent / rel).is_dir():
            return (parent / rel).resolve()
    # hard fallback to the known absolute location
    return Path(
        "/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/"
        "round_2/dataforge/datasets/steel-maintenance-flagship"
    )


LLMMode = Literal["cache_first", "live", "off"]
LLMProvider = Literal["subscription", "local_slm", "template"]


@dataclass(frozen=True)
class Settings:
    """Immutable runtime settings. Built once via `get_settings()`."""

    # --- paths ---
    dataset_root: Path
    package_root: Path
    demo_cache_path: Path

    # --- LLM ladder ---
    llm_mode: LLMMode = "cache_first"          # cache_first | live | off
    llm_provider: LLMProvider = "subscription"  # subscription | local_slm | template
    # Claude model strings (None => SDK default). Heavy = RCA/multiturn, light = diag/plan.
    model_heavy: str | None = None
    model_light: str | None = None
    # local SLM (Ollama) — keyless live fallback. Not load-bearing for the demo.
    slm_model: str = "qwen2.5:3b"
    slm_base_url: str = "http://127.0.0.1:11434"
    enable_slm: bool = False

    # --- timeouts (HARD per-rung; fail-forward fast) ---
    claude_timeout_s: float = 45.0
    slm_timeout_s: float = 60.0

    # --- dataset sub-paths (derived) ---
    spec_dir: Path = field(init=False)
    spine_path: Path = field(init=False)
    knowledge_dir: Path = field(init=False)
    equipment_manuals_dir: Path = field(init=False)
    sops_dir: Path = field(init=False)
    condition_dir: Path = field(init=False)
    operational_dir: Path = field(init=False)
    user_interaction_dir: Path = field(init=False)
    additional_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        ds = self.dataset_root
        object.__setattr__(self, "spec_dir", ds / "SPEC")
        object.__setattr__(self, "spine_path", ds / "SPEC" / "ground_truth_spine.json")
        object.__setattr__(self, "knowledge_dir", ds / "knowledge_docs")
        object.__setattr__(self, "equipment_manuals_dir", ds / "knowledge_docs" / "equipment_manuals")
        object.__setattr__(self, "sops_dir", ds / "knowledge_docs" / "maintenance_sops")
        object.__setattr__(self, "condition_dir", ds / "condition_monitoring")
        object.__setattr__(self, "operational_dir", ds / "operational_failure")
        object.__setattr__(self, "user_interaction_dir", ds / "user_interaction")
        object.__setattr__(self, "additional_dir", ds / "additional")

    # convenience flags ----------------------------------------------------
    @property
    def llm_enabled(self) -> bool:
        return self.llm_mode != "off" and self.llm_provider != "template"

    @property
    def has_oauth(self) -> bool:
        return bool(load_oauth_token())


def _bool_env(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


def _opt_env(name: str) -> str | None:
    v = os.getenv(name)
    return v if v else None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Build the singleton Settings. Resolves the OAuth token as a side effect."""
    # Make sure the token (and repo .env) is hydrated before anything LLM-y runs.
    load_oauth_token()

    package_root = Path(__file__).resolve().parent.parent  # .../vulcan/
    dataset_root = _default_dataset_root()
    demo_cache = Path(
        os.getenv("VULCAN_DEMO_CACHE", str(package_root / "data" / "demo" / "demo_cache.json"))
    )

    mode = os.getenv("VULCAN_LLM_MODE", "cache_first").strip().lower()
    if mode not in ("cache_first", "live", "off"):
        mode = "cache_first"
    provider = os.getenv("VULCAN_LLM_PROVIDER", "subscription").strip().lower()
    if provider not in ("subscription", "local_slm", "template"):
        provider = "subscription"

    return Settings(
        dataset_root=dataset_root,
        package_root=package_root,
        demo_cache_path=demo_cache,
        llm_mode=mode,            # type: ignore[arg-type]
        llm_provider=provider,    # type: ignore[arg-type]
        model_heavy=_opt_env("VULCAN_MODEL_HEAVY"),
        model_light=_opt_env("VULCAN_MODEL_LIGHT"),
        slm_model=os.getenv("VULCAN_SLM_MODEL", "qwen2.5:3b"),
        slm_base_url=os.getenv("VULCAN_SLM_BASE_URL", "http://127.0.0.1:11434"),
        enable_slm=_bool_env("VULCAN_ENABLE_SLM", False),
        claude_timeout_s=float(os.getenv("VULCAN_CLAUDE_TIMEOUT_S", "45")),
        slm_timeout_s=float(os.getenv("VULCAN_SLM_TIMEOUT_S", "60")),
    )


if __name__ == "__main__":  # quick smoke
    s = get_settings()
    print("VULCAN config")
    print("  dataset_root :", s.dataset_root, "exists=", s.dataset_root.is_dir())
    print("  spine_path   :", s.spine_path, "exists=", s.spine_path.is_file())
    print("  demo_cache   :", s.demo_cache_path)
    print("  llm_mode     :", s.llm_mode, "| provider:", s.llm_provider)
    print("  oauth token  :", "PRESENT" if s.has_oauth else "MISSING")
