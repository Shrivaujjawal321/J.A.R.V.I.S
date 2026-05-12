"""
Secure credential reader for browser-autopilot skill.

Reads platform credentials from .env (chmod 600). Never prints or logs the
value. Used by `workflows/login-flow.md`.

Convention:
  JARVIS_CRED_{PLATFORM}_EMAIL     e.g. JARVIS_CRED_LINKEDIN_EMAIL
  JARVIS_CRED_{PLATFORM}_PASSWORD  e.g. JARVIS_CRED_LINKEDIN_PASSWORD

CLI helpers (read-only, mask in output):
  python scripts/browser/credentials.py check linkedin    # prints "set" or "missing"
  python scripts/browser/credentials.py list              # which platforms have creds
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT / ".env")


class CredentialMissing(Exception):
    """Raised when a required credential is not in .env."""


def _env_key(platform: str, field: str) -> str:
    return f"JARVIS_CRED_{platform.upper()}_{field.upper()}"


def get_credential(platform: str, field: str) -> str:
    """Return the credential value. Raises CredentialMissing if not set.

    The value is NOT logged or echoed. Callers should pass it directly into the
    browser fill action and never store it elsewhere.
    """
    key = _env_key(platform, field)
    val = os.getenv(key)
    if not val:
        raise CredentialMissing(
            f"{key} not set in .env. "
            f"Boss must add it manually: echo '{key}=...' >> .env && chmod 600 .env"
        )
    return val


def has_credential(platform: str, field: str) -> bool:
    """Non-raising check."""
    return bool(os.getenv(_env_key(platform, field)))


def mask_email(email: str) -> str:
    """For audit logs: 'boss@example.com' -> 'b***@e***.com'."""
    if "@" not in email:
        return "***"
    local, _, domain = email.partition("@")
    masked_local = (local[0] + "***") if local else "***"
    if "." in domain:
        d_first, _, d_rest = domain.partition(".")
        masked_domain = (d_first[0] + "***." + d_rest) if d_first else f"***.{d_rest}"
    else:
        masked_domain = "***"
    return f"{masked_local}@{masked_domain}"


def list_configured_platforms() -> dict[str, dict[str, bool]]:
    """Scan env for all configured JARVIS_CRED_* platforms.

    Returns: {"linkedin": {"email": True, "password": True}, "naukri": {...}, ...}
    Never returns the values.
    """
    result: dict[str, dict[str, bool]] = {}
    prefix = "JARVIS_CRED_"
    for key in os.environ:
        if not key.startswith(prefix):
            continue
        rest = key[len(prefix):]
        parts = rest.rsplit("_", 1)
        if len(parts) != 2:
            continue
        platform, field = parts[0].lower(), parts[1].lower()
        result.setdefault(platform, {})[field] = True
    return result


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: credentials.py {check <platform> | list}")
        return 1
    cmd = sys.argv[1]
    if cmd == "check":
        if len(sys.argv) < 3:
            print("usage: credentials.py check <platform>")
            return 1
        platform = sys.argv[2]
        has_email = has_credential(platform, "email")
        has_pwd = has_credential(platform, "password")
        print(f"{platform}: email={'set' if has_email else 'missing'}, password={'set' if has_pwd else 'missing'}")
        return 0 if (has_email and has_pwd) else 2
    if cmd == "list":
        for plat, fields in sorted(list_configured_platforms().items()):
            field_str = ", ".join(f"{f}={'✓' if v else '✗'}" for f, v in sorted(fields.items()))
            print(f"  {plat:15} {field_str}")
        if not list_configured_platforms():
            print("  (none configured)")
        return 0
    print(f"unknown command: {cmd}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
