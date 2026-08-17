"""
CWE → OWASP → CVSS 4.0 lookup table.

All mappings are deterministic (no LLM). Scores computed via the `cvss`
library (CVSS4 class). Unknown CWEs fall back to a severity-bucketed
default vector.

CVSS 4.0 vector format:
  CVSS:4.0/AV:{N|A|L|P}/AC:{L|H}/AT:{N|P}/PR:{N|L|H}/UI:{N|P|A}/
           VC:{H|L|N}/VI:{H|L|N}/VA:{H|L|N}/
           SC:{H|L|N}/SI:{H|L|N}/SA:{H|L|N}
"""
from __future__ import annotations

import logging
from functools import lru_cache

log = logging.getLogger("jarvis_core.audit_agent.normalizers.cvss")

# ── CWE → CVSS 4.0 vector ─────────────────────────────────────────────────────
# Only the most common CWEs are enumerated. Unknown CWEs fall back to
# _severity_to_vector(). All vectors are defensively chosen for base score
# calculation — env/temporal not included (that's the verify layer's job).

_CWE_TO_VECTOR: dict[str, str] = {
    # Injection
    "CWE-89":  "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N",  # SQLi   9.3
    "CWE-78":  "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N",  # OS cmd 9.3
    "CWE-77":  "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N",  # Cmd inj
    "CWE-94":  "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H",  # Code inj
    "CWE-79":  "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N",  # XSS
    "CWE-611": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N",  # XXE
    "CWE-918": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N",  # SSRF
    # Path / file
    "CWE-22":  "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N",  # Path trav
    "CWE-73":  "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N",  # File name ctrl
    # Auth / credentials
    "CWE-798": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N",  # Hardcoded cred
    "CWE-259": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N",  # Hard pwd
    "CWE-321": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N",  # Hard crypto key
    "CWE-287": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N",  # Improper auth
    "CWE-306": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N",  # Missing auth
    "CWE-285": "CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N",  # Authz
    # Crypto
    "CWE-327": "CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N",  # Broken crypto
    "CWE-326": "CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N",  # Insuf. key
    "CWE-330": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N",  # Insuf. random
    # Deserialization / memory
    "CWE-502": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H",  # Unsafe deser
    "CWE-787": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N",  # OOB write
    "CWE-125": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N",  # OOB read
    # Misc
    "CWE-200": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N",  # Info disclosure
    "CWE-400": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N",  # ReDoS/DoS
    "CWE-601": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N",  # Open redirect
    "CWE-352": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N",  # CSRF
}

# CWE → OWASP 2025 category
_CWE_TO_OWASP: dict[str, str] = {
    "CWE-89":  "A05:2025-Injection",
    "CWE-78":  "A05:2025-Injection",
    "CWE-77":  "A05:2025-Injection",
    "CWE-94":  "A05:2025-Injection",
    "CWE-79":  "A05:2025-Injection",
    "CWE-611": "A05:2025-Injection",
    "CWE-918": "A05:2025-Injection",
    "CWE-22":  "A01:2025-BAC",
    "CWE-73":  "A01:2025-BAC",
    "CWE-798": "SECRETS",
    "CWE-259": "SECRETS",
    "CWE-321": "SECRETS",
    "CWE-287": "A01:2025-BAC",
    "CWE-306": "A01:2025-BAC",
    "CWE-285": "A01:2025-BAC",
    "CWE-327": "A04:2025-CryptoFail",
    "CWE-326": "A04:2025-CryptoFail",
    "CWE-330": "A04:2025-CryptoFail",
    "CWE-502": "A02:2025-Misconfig",
    "CWE-787": "A02:2025-Misconfig",
    "CWE-125": "A02:2025-Misconfig",
    "CWE-200": "A01:2025-BAC",
    "CWE-400": "A02:2025-Misconfig",
    "CWE-601": "A01:2025-BAC",
    "CWE-352": "A01:2025-BAC",
}

# Default vectors by severity bucket (fallback when CWE not in table)
_SEVERITY_DEFAULT_VECTORS: dict[str, str] = {
    "CRITICAL": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N",
    "HIGH":     "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N",
    "MEDIUM":   "CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N",
    "LOW":      "CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N",
    "INFO":     "CVSS:4.0/AV:L/AC:H/AT:N/PR:H/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N",
}

# SCA CVE severity → approximate CVSS vector
_CVE_SEVERITY_VECTORS: dict[str, str] = {
    "CRITICAL": _SEVERITY_DEFAULT_VECTORS["CRITICAL"],
    "HIGH":     _SEVERITY_DEFAULT_VECTORS["HIGH"],
    "MEDIUM":   _SEVERITY_DEFAULT_VECTORS["MEDIUM"],
    "LOW":      _SEVERITY_DEFAULT_VECTORS["LOW"],
    "UNKNOWN":  _SEVERITY_DEFAULT_VECTORS["LOW"],
}


# ── Public API ─────────────────────────────────────────────────────────────────


def cwe_to_cvss_vector(cwe: str | None) -> str | None:
    """Return the CVSS 4.0 vector for a given CWE ID, or None if unknown."""
    if not cwe:
        return None
    return _CWE_TO_VECTOR.get(cwe.upper())


def cwe_to_owasp(cwe: str | None) -> "OWASPCategory | None":
    """Return the OWASPCategory enum for a given CWE ID."""
    from ..models import OWASPCategory
    if not cwe:
        return OWASPCategory.UNKNOWN
    owasp_str = _CWE_TO_OWASP.get(cwe.upper(), "UNKNOWN")
    try:
        return OWASPCategory(owasp_str)
    except ValueError:
        return OWASPCategory.UNKNOWN


def severity_to_default_vector(severity: str) -> str:
    """Return a default CVSS 4.0 vector for a severity bucket."""
    return _SEVERITY_DEFAULT_VECTORS.get(severity.upper(), _SEVERITY_DEFAULT_VECTORS["MEDIUM"])


def cve_severity_to_cvss_vector(severity: str) -> str | None:
    """Return a CVSS 4.0 vector for a CVE severity string (for SCA findings)."""
    return _CVE_SEVERITY_VECTORS.get(severity.upper())


@lru_cache(maxsize=512)
def score_vector(vector: str | None) -> float | None:
    """Compute a CVSS 4.0 base score from a vector string.

    Returns None if the vector is invalid or None. Cached for performance.
    """
    if not vector:
        return None
    try:
        from cvss import CVSS4
        v = CVSS4(vector)
        return float(v.base_score)
    except Exception as exc:
        log.debug("CVSS4 score failed for %r: %s", vector, exc)
        return None
