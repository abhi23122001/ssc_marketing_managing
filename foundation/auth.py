"""Authentication foundation.

Session model: a random, one-time token issued at login; stored server-side in
the sessions table and sent to the client as `X-Session-Token` / `Authorization`.
Tokens are stateless over the transport (server-side revocation + expiry via
sessions.expires_at).  Password hashing uses PBKDF2-SHA256 (stdlib) and a
per-user random salt; substitution to bcrypt/argon2 is documented in
KNOWN-ISSUES.md.

No credentials are stored in code: the demo accounts used by the testing guide
are seeded only through the foundation config and flagged as local-dev placeholders.
"""

from __future__ import annotations

import time
from datetime import datetime

from .store import Store

# Legacy header names (the test client must honour the same names).
AUTH_HEADER = "Authorization"
TOKEN_PREFIX = "Bearer "


def issue_token(store: Store, username: str) -> str:
    u = store.get_user_by_username(username)
    if not u:
        raise KeyError("unknown user")
    expires_at = time.time() + 3600  # 1 hour local-dev
    token = store.create_session(u["id"], str(expires_at))
    return token


def authenticate(store: Store, token: str | None) -> dict[str, any] | None:
    if not token:
        return None
    if isinstance(token, str) and token.startswith(TOKEN_PREFIX):
        token = token[len(TOKEN_PREFIX):].strip()
    user = store.decode_session(token)
    if user is None:
        return None
    # Check token expiry
    expires_at = user.get("expires_at")
    if expires_at is None:
        return None
    try:
        # Handle numeric strings/timestamps (stored as text from float timestamps)
        if isinstance(expires_at, str):
            expires_at = expires_at.strip()
            # Try parsing as float first (handles "1795095448" and "1795100295.4709816")
            try:
                expires_time = float(expires_at)
            except ValueError:
                # Try ISO format
                try:
                    expires_time = time.mktime(datetime.strptime(expires_at, "%Y-%m-%dT%H:%M:%SZ").timetuple())
                except ValueError:
                    return None
        elif isinstance(expires_at, (int, float)):
            expires_time = float(expires_at)
        else:
            return None
        if expires_time < time.time():
            return None
    except (ValueError, TypeError, OSError):
        return None
    return user


def require_user(store: Store, token: str | None) -> dict[str, any]:
    user = authenticate(store, token)
    if user is None:
        raise PermissionError("authentication required")
    return user


def invalidate_session(store: Store, token: str | None) -> bool:
    """Invalidates/revokes a session token server-side upon logout."""
    if not token:
        return False
    if isinstance(token, str) and token.startswith(TOKEN_PREFIX):
        token = token[len(TOKEN_PREFIX):].strip()
    cur = store.conn.execute("DELETE FROM sessions WHERE token=?", (token,))
    store.conn.commit()
    return cur.rowcount > 0


def revoke_user_sessions(store: Store, user_id: int) -> int:
    """Revokes all active sessions for a user (e.g. after password change or deactivation)."""
    cur = store.conn.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
    store.conn.commit()
    return cur.rowcount


def change_user_password(
    store: Store, user_id: int, old_password: str, new_password: str
) -> tuple[bool, str]:
    """Securely rotates user password with complexity validation and session invalidation."""
    u = store.get_user_by_id(user_id)
    if not u:
        return False, "User not found"

    # Verify old password
    from .store import _verify, _pbkdf2
    if not _verify(old_password, u["password_hash"]):
        return False, "Current password verification failed"

    # Complexity check: min 8 chars, at least 1 digit or special character
    if len(new_password) < 8:
        return False, "New password must be at least 8 characters long"
    if not any(c.isdigit() or not c.isalnum() for c in new_password):
        return False, "New password must contain at least one digit or special character"

    # Update hash
    store.update_user(user_id, password=new_password)
    # Revoke sessions
    revoke_user_sessions(store, user_id)
    return True, "Password rotated successfully. All active sessions invalidated."

