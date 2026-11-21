"""Shared helpers used across the domain layer.

These small routines are kept in a single place so that business modules never
drift apart on workspace isolation, audit logging or time utilities.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from ..store import Store


def _workspace_exists(store: Store, workspace_id: str) -> bool:
    return store.conn.execute(
        "SELECT 1 FROM workspaces WHERE id=? OR code=?", (workspace_id, workspace_id)
    ).fetchone() is not None


def _assert_owned(store: Store, actor_id: int, workspace_id: str) -> None:
    row = store.conn.execute(
        "SELECT u.workspace_id, r.code AS code FROM users u "
        "JOIN roles r ON r.id = u.role_id WHERE u.id=?",
        (actor_id,),).fetchone()
    if not row:
        raise PermissionError("unknown actor")
    if row["code"] != "Owner" and row["workspace_id"] != workspace_id:
        raise PermissionError(
            f"workspace isolation: actor {actor_id} belongs to "
            f"{row['workspace_id']!r}, not {workspace_id!r}")


def _audit(store: Store, actor_id: int, action: str, target: str,
           details: dict, workspace_id: str | None) -> int:
    return store.add_audit(actor_id, action, target, details, workspace_id)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _json_dumps(obj) -> str:
    return json.dumps(obj) if obj is not None else "{}"
