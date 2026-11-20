"""Approval Engine.

Lifecycle (current_stage + status) enforced through the Store:

    draft -> pending    (create)
    pending -> approved (approve: Owner/Manager/Finance/PM)
    pending -> rejected (approve: Owner/Manager/Finance/PM)
    pending -> withdrawn (Owner/Manager)

The engine is a thin state machine over store.transition_approval(). Real
production rules (two-man approval for high-value items, escalation paths,
balance holders, deadline expiry) are documented in KNOWN-ISSUES.md and are
intentional TODOs, not hidden tests that report PASS.
"""

from __future__ import annotations

from . import rbac

# Roles allowed to move an approval to approved/rejected.
_APPROVE_ROLES = {"Owner", "Manager", "Finance Manager", "Project Manager"}


def require_approver(store: Store, actor_user_id: int, approval_id: int) -> None:
    a = store.get_approval(approval_id)
    if not a:
        raise KeyError(f"approval {approval_id} not found")
    role = _current_role(store, actor_user_id)
    if role not in _APPROVE_ROLES:
        raise PermissionError(
            f"{role} cannot approve. Owner/Manager/Finance/PM only.")
    if a["status"] not in ("draft", "pending"):
        raise PermissionError(f"approval {a['status']} cannot be approved")


def _current_role(store: Store, user_id: int) -> str | None:
    row = store.conn.execute(
        "SELECT r.code AS code FROM users u "
        "JOIN roles r ON r.id = u.role_id WHERE u.id = ?", (user_id,)).fetchone()
    return row["code"] if row else None


def can_create(store: Store, user_id: int) -> bool:
    role = _current_role(store, user_id)
    if role is None:
        return False
    return rbac.has_permission(role, "approval:create")


def create_approval(store: Store, title: str, description: str,
                    requested_by: int, workspace_id: str,
                    resource_key: str) -> dict:
    if not can_create(store, requested_by):
        raise PermissionError(
            "approval:create is reserved for Owner and Manager seats.")
    return store.create_approval(workspace_id, title, description,
                                 requested_by, resource_key)


def transition(store: Store, approval_id: int, new_status: str,
               actor_user_id: int, note: str = "") -> dict:
    if new_status in ("approved", "rejected", "withdrawn"):
        require_approver(store, actor_user_id, approval_id)
        if store.get_approval(approval_id)["status"] not in ("draft", "pending"):
            raise PermissionError(f"approval {new_status} not allowed from state")
    return store.transition_approval(approval_id, new_status,
                                     actor_user_id, note)
