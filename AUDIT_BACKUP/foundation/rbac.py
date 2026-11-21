"""Role-based access control.

Permission vocabulary (flat namespaces so roles map unambiguously to the
seven-seat matrix the architecture requires):

    workspace:list/ read / manage
    resource:list/read/create/edit/delete
    approval:list/read/approve/comment
    audit:list/read
    report:list/read
    ai:brain:query

Role->permission table:
    Owner          -> ["*"] (everything)
    Manager        -> full management + approvals + audit/report
    Project Manager-> resource mgmt, approvals, read-only reporting
    Finance Manager-> resources + approvals + finance-aware reporting
    HR Manager     -> resources + approvals + HR reporting
    Employee       -> read + comment on approvals
    Viewer         -> read-only
"""

from __future__ import annotations

import json
from typing import Any

from . import config as foundation_config


def all_permissions() -> dict[str, str]:
    """Return the permission vocabulary (slug -> description)."""
    cfg = foundation_config.load_config()
    return dict(cfg.get("permissions", {}))


def role_permission_codes() -> dict[str, list[str]]:
    cfg = foundation_config.load_config()
    out = {}
    for code, perms in cfg.get("roles_permissions", {}).items():
        out[code] = list(perms)
    return out


def all_role_codes() -> list[str]:
    cfg = foundation_config.load_config()
    return [r["code"] for r in cfg.get("roles", [])]


def resolve_user_permissions(role_code: str) -> list[str]:
    codes = role_permission_codes()
    perms = codes.get(role_code, [])
    if "*" in perms or "*" in [p for p in perms if p in codes]:
        return sorted(set(all_permissions().keys()))
    return perms


def has_permission(role_code: str, permission: str) -> bool:
    return permission in resolve_user_permissions(role_code)


def seven_role_matrix() -> dict[str, dict[str, Any]]:
    """Return a human-readable role-permission matrix."""
    out = {}
    for role in all_role_codes():
        out[role] = {
            "seat": next((r["seat"] for r in foundation_config.load_config()["roles"] if r["code"] == role), None),
            "permissions": role_permission_codes()[role],
        }
    return out
