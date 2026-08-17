"""
supa/auth.py — FastAPI dependency for Supabase JWT verification.

Key system: Supabase new-style keys (sb_publishable_ / sb_secret_).
Tokens issued by Supabase Auth use ES256 (ECDSA P-256).
We verify via JWKS fetched from the project's .well-known endpoint.

JWKS is cached in-process with a 1-hour TTL; fetch is lazy on first request.

Falls back gracefully:
  - If EDITH_AUTH_REQUIRED=0 and no token: returns anonymous UserContext
  - If EDITH_AUTH_REQUIRED=1 and no token: raises 401

Thread-safe JWKS cache using a threading.Lock.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from threading import Lock
from typing import Optional

import httpx
from fastapi import Header, HTTPException

# PyJWT 2.x + cryptography — ES256 support is built-in
import jwt as pyjwt
from jwt import PyJWKClient

# ── Config ────────────────────────────────────────────────────────────────────
SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
JWKS_CACHE_TTL = 3600  # 1 hour

AUTH_REQUIRED: bool = os.environ.get("EDITH_AUTH_REQUIRED", "0").lower() in ("1", "true", "yes")

# ── JWKS cache ────────────────────────────────────────────────────────────────
_jwks_client: Optional[PyJWKClient] = None
_jwks_fetched_at: float = 0.0
_jwks_lock = Lock()


def _get_jwks_client() -> PyJWKClient:
    """Return a cached PyJWKClient, refreshing after JWKS_CACHE_TTL seconds."""
    global _jwks_client, _jwks_fetched_at
    now = time.monotonic()
    if _jwks_client is None or (now - _jwks_fetched_at) > JWKS_CACHE_TTL:
        with _jwks_lock:
            if _jwks_client is None or (now - _jwks_fetched_at) > JWKS_CACHE_TTL:
                # PyJWKClient handles fetching and caching keys itself;
                # we wrap it with our own TTL so we can force-refresh.
                _jwks_client = PyJWKClient(JWKS_URL, cache_keys=True, lifespan=JWKS_CACHE_TTL)
                _jwks_fetched_at = now
    return _jwks_client


# ── UserContext ───────────────────────────────────────────────────────────────
@dataclass
class UserContext:
    user_id: str           # UUID string from JWT sub
    email: Optional[str]
    role: str              # "authenticated" | "anon" | "service_role"
    is_anonymous: bool = False


ANONYMOUS_USER = UserContext(
    user_id="anonymous",
    email=None,
    role="anon",
    is_anonymous=True,
)


# ── Error helpers ─────────────────────────────────────────────────────────────
def _auth_error(message: str, code: str = "unauthorized") -> HTTPException:
    return HTTPException(
        status_code=401,
        detail={
            "error": {
                "code": code,
                "message": message,
                "type": "auth",
            }
        },
    )


# ── JWT verification ──────────────────────────────────────────────────────────
def _verify_jwt(token: str) -> UserContext:
    """
    Verify a Supabase-issued JWT.
    Primary path: ES256 via JWKS.
    Raises HTTPException 401 on any failure.
    """
    try:
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = pyjwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],  # ES256 for new Supabase, RS256 for legacy
            audience="authenticated",
            options={"verify_exp": True},
        )
        return UserContext(
            user_id=payload["sub"],
            email=payload.get("email"),
            role=payload.get("role", "authenticated"),
            is_anonymous=False,
        )
    except pyjwt.ExpiredSignatureError:
        raise _auth_error("Token expired. Please sign in again.")
    except pyjwt.InvalidAudienceError:
        raise _auth_error("Token audience mismatch.")
    except pyjwt.InvalidTokenError as exc:
        raise _auth_error(f"Invalid token: {exc}")
    except Exception as exc:
        # JWKS fetch failure, network issue, etc.
        raise _auth_error(f"Token verification failed: {type(exc).__name__}")


# ── FastAPI dependencies ──────────────────────────────────────────────────────
async def get_current_user(
    authorization: Optional[str] = Header(default=None),
) -> Optional[UserContext]:
    """
    Optional auth dependency.
    - Token present and valid → UserContext
    - No token → None (public route access)
    - Token present but invalid → 401
    """
    if not authorization:
        return None
    if not authorization.startswith("Bearer "):
        raise _auth_error("Authorization header must be 'Bearer <token>'")
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise _auth_error("Empty bearer token.")
    return _verify_jwt(token)


async def require_user(
    authorization: Optional[str] = Header(default=None),
) -> UserContext:
    """
    Mandatory auth dependency.
    Respects EDITH_AUTH_REQUIRED flag:
      - flag=1: enforces auth always
      - flag=0: allows anonymous through (for back-compat during migration)
    """
    if not AUTH_REQUIRED:
        # Back-compat mode: try to verify if token present, else allow anonymous
        user = await get_current_user(authorization)
        if user is not None:
            return user
        return ANONYMOUS_USER

    # AUTH_REQUIRED=1: strict enforcement
    user = await get_current_user(authorization)
    if user is None:
        raise _auth_error("Authentication required. Provide a Supabase Bearer token.")
    return user
