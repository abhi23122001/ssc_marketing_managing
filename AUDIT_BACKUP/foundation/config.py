"""Configuration for the SHAH Group AI OS foundation.

Configuration is plain JSON so it is editor-friendly and never needs a
third-party dependency. All values have safe defaults derived from the
required architecture:

  - Three business workspaces: SSC | INFRA | OTHER
  - Seven roles: Owner, Manager, Project Manager, Finance Manager, HR Manager,
    Employee, Viewer
  - Stdlib-only runtime (sqlite3, hashlib, http.server, json, threading)
"""

from __future__ import annotations

import json
from pathlib import Path

DEFAULT_CONFIG = {
    "db_path": "data/sgcc_foundation.sqlite",
    "port": 8899,
    "host": "127.0.0.1",
    "seed_demo_users": True,
    # The AI-brain identity used by orchestration notes. Local-only.
    "ai_brain": {
        "name": "SHAH Brain",
        "mode": "local",
        "prompt_prefix": "You are the shared AI Brain for Shah Surveyors & Consultancy "
                        "workspaces (SSC, INFRA, OTHER). You answer from the "
                        "project context and never invent client or project facts.",
    },
    "workspaces": [
        {"code": "SSC", "label": "Shah Surveyors & Consultancy", "is_isolated": True},
        {"code": "INFRA", "label": "Contracted / Infra Works", "is_isolated": True},
        {"code": "OTHER", "label": "Other / Reference Workspace", "is_isolated": False},
    ],
    "roles": [
        {"code": "Owner", "label": "Owner", "seat": "owner"},
        {"code": "Manager", "label": "Manager", "seat": "manager"},
        {"code": "Project Manager", "label": "Project Manager", "seat": "pm"},
        {"code": "Finance Manager", "label": "Finance Manager", "seat": "finance"},
        {"code": "HR Manager", "label": "HR Manager", "seat": "hr"},
        {"code": "Employee", "label": "Employee", "seat": "employee"},
        {"code": "Viewer", "label": "Viewer", "seat": "viewer"},
    ],
    "permissions": {
        "workspace:list": "List all workspaces",
        "workspace:read": "Read a workspace",
        "workspace:manage": "Create / edit / archive a workspace",
        "resource:list": "List resources",
        "resource:read": "Read a resource",
        "resource:create": "Create a resource",
        "resource:edit": "Edit a resource",
        "resource:delete": "Delete a resource",
        "approval:list": "List approvals",
        "approval:read": "Read a specific approval",
        "approval:approve": "Approve or reject an approval",
        "approval:comment": "Comment on an approval",
        "approval:create": "Create an approval",
        "approval:delete": "Delete an approval",
        "audit:list": "List audit entries",
        "audit:read": "Read a specific audit entry",
        "report:list": "List reports",
        "report:read": "Read a report",
        "report:generate": "Generate reports from workspace data",
        "ai:brain:query": "Query the shared AI Brain",
        "employees:read": "Read employees in workspace",
        "attendance:read": "Read attendance logs",
        "expense:read": "Read expense claims",
        "payroll:read": "Read payroll runs",
    },
    "roles_permissions": {
        "Owner": ["*"],
        "Manager": [
            "workspace:list", "workspace:read", "workspace:manage",
            "resource:list", "resource:read", "resource:create", "resource:edit", "resource:delete",
            "approval:list", "approval:read", "approval:approve", "approval:comment",
            "audit:list", "report:list", "report:read", "ai:brain:query",
        ],
        "Project Manager": [
            "workspace:read", "resource:list", "resource:read", "resource:create", "resource:edit",
            "approval:list", "approval:read", "approval:comment",
            "report:list", "report:read", "ai:brain:query",
        ],
        "Finance Manager": [
            "workspace:read", "resource:list", "resource:read",
            "approval:list", "approval:read", "approval:approve", "approval:comment",
            "report:list", "report:read", "ai:brain:query",
        ],
        "HR Manager": [
            "workspace:read", "resource:list", "resource:read",
            "approval:list", "approval:read", "approval:comment",
            "report:list", "report:read", "ai:brain:query",
        ],
        "Employee": [
            "workspace:read", "resource:list", "resource:read",
            "approval:list", "approval:read", "approval:comment",
            "report:list", "report:read", "ai:brain:query",
        ],
        "Viewer": [
            "workspace:read", "resource:list", "resource:read", "ai:brain:query",
        ],
    },
    # Demo accounts used by the testing guide. These are plain-text placeholders
    # for local development only; KNOWN-ISSUES.md requires the owner to rotate
    # them before any internal or client-facing use.
    "demo_users": [
        {"username": "owner", "password": "demo-owner-pass-0001", "name": "Owner Person",
         "workspace": "SSC", "role": "Owner"},
        {"username": "manager", "password": "demo-manager-pass-0001", "name": "Manager Person",
         "workspace": "SSC", "role": "Manager"},
        {"username": "employee", "password": "demo-employee-pass-0001", "name": "Employee Person",
         "workspace": "SSC", "role": "Employee"},
        {"username": "viewer", "password": "demo-viewer-pass-0001", "name": "Viewer Person",
         "workspace": "INFRA", "role": "Viewer"},
        {"username": "finance", "password": "demo-finance-pass-0001", "name": "Finance Person",
         "workspace": "INFRA", "role": "Finance Manager"},
        {"username": "pm", "password": "demo-pm-pass-0001", "name": "Project Manager Person",
         "workspace": "INFRA", "role": "Project Manager"},
        {"username": "hr", "password": "demo-hr-pass-0001", "name": "HR Person",
         "workspace": "OTHER", "role": "HR Manager"},
    ],
}

# ---------------------------------------------------------------------------
# Path helpers. Working directory is the project root (ssc_marketing_managing).
# ---------------------------------------------------------------------------

def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def config_path() -> Path:
    return project_root() / "foundation" / "config.json"


def load_config() -> dict:
    """Load foundation config, merging DEFAULT_CONFIG with foundation/config.json."""
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    p = config_path()
    if p.is_file():
        try:
            user = json.loads(p.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            user = {}
        _deep_merge(cfg, user)
    return cfg


def _deep_merge(base: dict, override: dict) -> None:
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v
