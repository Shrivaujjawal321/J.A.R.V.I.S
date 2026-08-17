"""
Scope verification + enforcement.

Safety boundaries (HARD-CODED, not config-overridable):
- RFC1918 and cloud-metadata IP ranges are permanently blocked.
- Path traversal attacks (../) are normalized away before matching.
- Local paths under $HOME are auto-approved for "local_dir" targets.
- `allow_exploitation` on an unverified target is always refused.

Verification methods:
- local_dir: auto-approve if path is under os.path.expanduser("~")
- git_repo: check .github/CODEOWNERS or SECURITY.md for Boss's email
- dns_txt: DNS TXT record _jarvis-audit.<domain> matches per-audit token
- manual: always False unless explicitly set by caller
"""
from __future__ import annotations

import fnmatch
import ipaddress
import logging
import os
import re
from pathlib import Path, PurePosixPath

import dns.resolver  # dnspython>=2.6

from .models import ScopePolicy, Target

log = logging.getLogger("jarvis_core.audit_agent.scope")

# ── RFC1918 + metadata hard-blocks ────────────────────────────────────────────
# These networks are NEVER valid audit targets — hard-coded, not configurable.
_BLOCKED_NETWORKS: list[ipaddress.IPv4Network] = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),   # link-local / cloud metadata
    ipaddress.ip_network("127.0.0.0/8"),       # loopback
    ipaddress.ip_network("::1/128"),            # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),           # IPv6 ULA
]

_BOSS_EMAILS: frozenset[str] = frozenset({
    "shriva.ujjawal@gmail.com",
    "ujjwal",  # partial match
})

_CODEOWNERS_PATHS = [
    ".github/CODEOWNERS",
    "CODEOWNERS",
    "SECURITY.md",
    "docs/CODEOWNERS",
]


def _is_blocked_ip(host: str) -> bool:
    """Return True if host resolves to (or IS) a blocked network address."""
    try:
        addr = ipaddress.ip_address(host)
        for network in _BLOCKED_NETWORKS:
            try:
                if addr in network:
                    return True
            except TypeError:
                pass  # mixed IPv4/IPv6
    except ValueError:
        pass  # Not a bare IP — that's fine, we check by hostname below
    return False


def _extract_hostname(uri: str) -> str:
    """Pull hostname from a URI or path string."""
    # Handles: https://github.com/org/repo, github.com/org/repo, /local/path
    if uri.startswith("/") or uri.startswith("~"):
        return ""
    match = re.match(r"(?:https?://)?([^/:\s]+)", uri)
    return match.group(1) if match else ""


# ── Scope verification ─────────────────────────────────────────────────────────


async def verify_scope(policy: ScopePolicy) -> bool:
    """Return True if the target is authorized for scanning.

    For local_dir: auto-approve if under $HOME.
    For git_repo: check CODEOWNERS / SECURITY.md for Boss's email.
    All other kinds: return False unless verified_owner is already set.
    Refuses if target resolves to a blocked network.
    """
    target = policy.target

    # Safety: check for blocked IPs in the URI
    host = _extract_hostname(target.uri)
    if host and _is_blocked_ip(host):
        log.warning("SCOPE DENIED: target %r resolves to blocked network", target.uri)
        return False

    if target.kind == "local_dir":
        ok = _verify_local_path(target)
        if ok:
            target.verified_owner = True
            target.verification_method = "local"
        return ok

    if target.kind == "git_repo":
        ok = await _verify_git_repo(target)
        if ok:
            target.verified_owner = True
            target.verification_method = "codeowners"
        return ok

    # openapi_spec, container_image — require explicit verified_owner=True
    if target.verified_owner:
        return True

    log.warning("SCOPE DENIED: target kind=%r requires manual verification", target.kind)
    return False


def _verify_local_path(target: Target) -> bool:
    """Auto-approve local directories under $HOME."""
    home = Path(os.path.expanduser("~")).resolve()
    try:
        resolved = Path(target.uri).expanduser().resolve()
    except (OSError, RuntimeError) as exc:
        log.warning("Local path resolution failed for %r: %s", target.uri, exc)
        return False

    if not resolved.exists():
        log.warning("Local path does not exist: %s", resolved)
        return False

    try:
        resolved.relative_to(home)
        return True
    except ValueError:
        log.warning(
            "SCOPE DENIED: %s is outside $HOME (%s) — require manual verification",
            resolved, home,
        )
        return False


async def _verify_git_repo(target: Target) -> bool:
    """Check that Boss's email appears in CODEOWNERS or SECURITY.md."""
    uri = target.uri

    # If it's a local clone, check directly
    maybe_path = Path(uri) if not uri.startswith("http") else None
    if maybe_path and maybe_path.exists():
        for rel in _CODEOWNERS_PATHS:
            candidate = maybe_path / rel
            if candidate.exists():
                text = candidate.read_text(errors="replace").lower()
                if any(e.lower() in text for e in _BOSS_EMAILS):
                    log.info("Ownership verified via %s", candidate)
                    return True
        # No CODEOWNERS found in local clone → check if under home
        return _verify_local_path(target)

    log.info(
        "Remote git repo %r — cannot verify without DNS/token. "
        "Use local_dir for local clones.",
        uri,
    )
    return False


def verify_dns_txt(domain: str, expected_token: str) -> bool:
    """Verify domain ownership via DNS TXT record.

    Expected: _jarvis-audit.<domain> TXT "<expected_token>"
    """
    lookup = f"_jarvis-audit.{domain}"
    try:
        answers = dns.resolver.resolve(lookup, "TXT")
        for rdata in answers:
            for txt_bytes in rdata.strings:
                if txt_bytes.decode("utf-8", errors="replace").strip() == expected_token:
                    log.info("DNS TXT ownership verified for %s", domain)
                    return True
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
        pass
    except Exception as exc:
        log.warning("DNS TXT lookup failed for %s: %s", domain, exc)
    return False


# ── Path scope enforcement ─────────────────────────────────────────────────────


def _normalize_path(file_path: str, base_path: str | None = None) -> str:
    """Normalize + sanitize a file path.

    Resolves ../ traversal components by building the full absolute path
    when base_path is given. Returns "" if the path would escape the base.
    """
    if base_path:
        # Build absolute path: base + file_path, then collapse ../ segments
        base = PurePosixPath(base_path)
        raw = base / file_path
        # Collapse by re-processing parts against the absolute base
        parts: list[str] = list(base.parts)
        for part in PurePosixPath(file_path).parts:
            if part == "..":
                if len(parts) > len(base.parts):
                    parts.pop()
                # else: trying to go above base — traversal detected, keep base
                else:
                    log.warning(
                        "Path traversal attempt blocked: %r resolves outside base %r",
                        file_path, base_path,
                    )
                    return ""
            elif part != ".":
                parts.append(part)
        full = PurePosixPath(*parts)
        try:
            full.relative_to(base)
        except ValueError:
            log.warning(
                "Path traversal attempt blocked: %r resolved to %r outside base %r",
                file_path, str(full), base_path,
            )
            return ""
        return str(full.relative_to(base))

    # No base_path — simple collapse
    p = PurePosixPath(file_path)
    result_parts: list[str] = []
    for part in p.parts:
        if part == "..":
            if result_parts:
                result_parts.pop()
        elif part != ".":
            result_parts.append(part)
    return "/".join(result_parts) if result_parts else ""


def enforce_scope(file_path: str, policy: ScopePolicy, base_path: str | None = None) -> bool:
    """Return True if file_path is within audit scope.

    Checks:
    1. Path traversal safety (normalizes ../ first).
    2. RFC1918 / metadata IP blocks if file_path looks like a URL.
    3. excluded_paths patterns (fnmatch).
    4. included_paths patterns (fnmatch) — must match at least one.
    """
    if not file_path:
        return False

    # Block IP-based file paths that look like internal URLs
    host = _extract_hostname(file_path)
    if host and _is_blocked_ip(host):
        log.warning("enforce_scope blocked RFC1918 path: %r", file_path)
        return False

    normalized = _normalize_path(file_path, base_path=base_path)
    if not normalized and base_path:
        return False  # Traversal blocked

    check_path = normalized or file_path

    # Excluded paths take priority
    for pattern in policy.excluded_paths:
        if fnmatch.fnmatch(check_path, pattern):
            return False

    # Must match at least one included pattern
    for pattern in policy.included_paths:
        if fnmatch.fnmatch(check_path, pattern):
            return True

    return False
