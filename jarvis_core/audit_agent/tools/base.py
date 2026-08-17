"""
ToolAdapter ABC + subprocess runner helper.

All scanner adapters inherit from ToolAdapter. The run() method executes
a subprocess CLI tool and returns a RawScanResult. normalize() parses the
raw output into canonical Finding objects.

Graceful degradation contract:
- If the binary is not installed (FileNotFoundError), return RawScanResult
  with error="not_installed" — the run CONTINUES with other adapters.
- If the process times out, kill it and return error="timeout".
- If JSON output is unparseable, return empty findings (normalize logs a warning).
- Non-zero exit codes are logged but NOT raised — many scanners exit 1 on findings.
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel

from ..models import Finding, RawScanResult

log = logging.getLogger("jarvis_core.audit_agent.tools")


# ── Tool I/O ───────────────────────────────────────────────────────────────────


class ToolInput(BaseModel):
    target_path: str                    # absolute path to repo / file / dir
    extra_args: list[str] = []
    timeout_seconds: int = 120
    env_overrides: dict[str, str] = {}


class ToolTimeoutError(Exception):
    pass


class ToolError(Exception):
    pass


# ── Subprocess helper ──────────────────────────────────────────────────────────


async def _run_subprocess(
    cmd: list[str],
    *,
    timeout_seconds: int = 120,
    env_overrides: dict[str, str] | None = None,
    cwd: str | None = None,
) -> tuple[int, str, str]:
    """Run a subprocess, return (returncode, stdout, stderr).

    Raises ToolTimeoutError if timeout exceeded (kills process first).
    Raises ToolError for OS-level errors other than FileNotFoundError.
    Raises FileNotFoundError if binary is not on PATH — caller handles.
    """
    env = {**os.environ, **(env_overrides or {})}
    started = time.perf_counter()

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            cwd=cwd,
        )
    except FileNotFoundError:
        raise  # Caller catches this as "not_installed"
    except OSError as exc:
        raise ToolError(f"OS error launching {cmd[0]!r}: {exc}") from exc

    try:
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(), timeout=timeout_seconds
        )
    except asyncio.TimeoutError:
        try:
            proc.kill()
            await proc.wait()
        except ProcessLookupError:
            pass
        elapsed = int((time.perf_counter() - started) * 1000)
        raise ToolTimeoutError(
            f"{cmd[0]!r} timed out after {timeout_seconds}s ({elapsed}ms)"
        )

    return (
        proc.returncode or 0,
        stdout_bytes.decode("utf-8", errors="replace"),
        stderr_bytes.decode("utf-8", errors="replace"),
    )


# ── ToolAdapter ABC ────────────────────────────────────────────────────────────


class ToolAdapter(ABC):
    name: str               # "semgrep" | "trivy" | "osv" | "gitleaks" | "trufflehog"
    scanner_type: str       # "sast" | "sca" | "secrets" | "container"
    default_timeout: int = 120   # per-adapter timeout; SAST (semgrep) overrides higher

    @abstractmethod
    async def run(self, inp: ToolInput) -> RawScanResult:
        """Execute scanner CLI, return raw result. NEVER raises — all errors captured."""
        ...

    @abstractmethod
    def normalize(self, raw: RawScanResult) -> list[Finding]:
        """Parse scanner-specific JSON → canonical Finding list."""
        ...

    async def run_and_normalize(self, inp: ToolInput) -> list[Finding]:
        """Convenience: run + normalize in one call. Returns [] on any error."""
        raw = await self.run(inp)
        if raw.error:
            log.warning(
                "scanner=%s skipped normalization due to error: %s",
                self.name, raw.error,
            )
            return []
        return self.normalize(raw)

    def _make_error_result(self, error: str) -> RawScanResult:
        return RawScanResult(scanner=self.name, exit_code=-1, error=error)
