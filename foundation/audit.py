"""Audit logging.

Every meaningful action (login, workspace/scoped read/write, approval move,
token revoke) is written to audit_logs with: actor, action, target, details
and workspace.  Audit feeds are themselves workspace-scoped so no business data
leaves its domain.

Audit entries are append-only by design; the API does not expose a delete.
"""

from __future__ import annotations

import time

from .store import Store


def log(store: Store, actor_id: int, action: str, target: str, details: dict | None = None,
        workspace_id: str | None = None) -> int:
    return store.add_audit(actor_id, action, target, details, workspace_id)


def log_if_authenticated(store: Store, actor: dict, action: str, target: str,
                         details: dict | None = None) -> int | None:
    if actor is None:
        return None
    return log(store, actor["user_id"], action, target, details, actor.get("workspace_id"))


def audit_summary(store: Store, workspace_id: str, limit: int = 50) -> dict:
    rows = store.list_audit(workspace_id)
    return {"workspace": workspace_id, "count": len(rows), "rows": rows[:limit]}
