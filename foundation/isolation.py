"""Business-level data isolation.

Every business workspace (SSC / INFRA / OTHER) is an isolated data domain.
The rule, enforced in the store and the API:

  A user may only touch records whose workspace_id matches their own workspace.
  A user belongs to exactly one workspace at query time.

Special case: the Owner and other "system" actors carrying workspace_id=None MAY
read across workspaces for consolidated reporting — that is the intended
Owner-authorized consolidated reporting path and it is logged to audit.

The isolation test (foundation/tests/test_isolation.py) asserts this at the
query level: an INFRA Viewer cannot list INFRA resources through an SSC session
and vice versa.

Workspaces are "separate business workspaces" per the architecture; notes and
reports are the shared orchestration seam, not the underlying business data.
"""

from __future__ import annotations

from .store import Store


def user_workspace(store: Store, user: dict) -> str | None:
    return user.get("workspace_id")


def is_isolated(store: Store, workspace_code: str) -> bool:
    w = store.get_workspace(workspace_code)
    return bool(w and w.get("is_isolated"))


def resolve_scope(store: Store, user: dict, default_workspace: str | None = None):
    """Return the (workspace_id or None) the user may operate against.

    Owner / system actor -> None (all workspaces, consolidated).
    Member actor -> their own workspace (isolated).
    """
    if user.get("workspace_id") is None:
        # Owner + explicit system scope
        return None
    return user.get("workspace_id")


def assert_isolated_to(store: Store, user: dict, workspace_code: str) -> str:
    """Return the workspace_id the user may query. Raises PermissionError if the
    target workspace differs from the user's own and the user is not the owner."""
    my = user.get("workspace_id")
    target = workspace_code.lower()
    if my is None:
        return None  # Owner scope: no isolation gate
    if my == target:
        return my
    raise PermissionError(
        f"isolation blocked: user {user['username']!r} (workspace={my}) "
        f"cannot access {target!r}")
