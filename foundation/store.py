"""SQLite-backed persistence layer (stdlib only).

Stores:
  users, roles, workspaces, resources, approvals, audit_logs, sessions

All query helpers are workspace-scoped: a user is always limited to the
workspace they belong to, except the Owner who can reach every workspace.
This is the enforcement point for "business-level data isolation".
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import re
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import config as foundation_config
from .approval import require_approver

_PBKD = 100_000  # pbkdf2 iterations (local dev, swappable to bcrypt later)


class _ThreadSafeCursor:
    def __init__(self, cur: sqlite3.Cursor, lock: threading.RLock):
        self._cur = cur
        self._lock = lock

    def fetchone(self):
        with self._lock:
            return self._cur.fetchone()

    def fetchall(self):
        with self._lock:
            return self._cur.fetchall()

    def fetchmany(self, size=None):
        with self._lock:
            return self._cur.fetchmany(size) if size is not None else self._cur.fetchmany()

    def __iter__(self):
        with self._lock:
            return iter(self._cur.fetchall())

    def __getattr__(self, name: str):
        return getattr(self._cur, name)


class _ThreadSafeConnection:
    def __init__(self, conn: sqlite3.Connection):
        self._raw_conn = conn
        self._lock = threading.RLock()

    @property
    def row_factory(self):
        return self._raw_conn.row_factory

    @row_factory.setter
    def row_factory(self, val):
        with self._lock:
            self._raw_conn.row_factory = val

    def execute(self, *args, **kwargs):
        with self._lock:
            cur = self._raw_conn.execute(*args, **kwargs)
            return _ThreadSafeCursor(cur, self._lock)

    def executemany(self, *args, **kwargs):
        with self._lock:
            cur = self._raw_conn.executemany(*args, **kwargs)
            return _ThreadSafeCursor(cur, self._lock)

    def executescript(self, *args, **kwargs):
        with self._lock:
            cur = self._raw_conn.executescript(*args, **kwargs)
            return _ThreadSafeCursor(cur, self._lock)

    def cursor(self, *args, **kwargs):
        with self._lock:
            cur = self._raw_conn.cursor(*args, **kwargs)
            return _ThreadSafeCursor(cur, self._lock)

    def commit(self):
        with self._lock:
            return self._raw_conn.commit()

    def rollback(self):
        with self._lock:
            return self._raw_conn.rollback()

    def close(self):
        with self._lock:
            return self._raw_conn.close()

    def __getattr__(self, name: str):
        return getattr(self._raw_conn, name)

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            return self._raw_conn.__exit__(exc_type, exc_val, exc_tb)
        finally:
            self._lock.release()



def json_dumps(obj: Any) -> str:
    import json
    return json.dumps(obj) if obj is not None else ""


def _pbkdf2(password: str) -> str:
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKD)
    return "pbkdf2${}${}".format(salt.hex(), dk.hex())


def _verify(password: str, stored: str) -> bool:
    try:
        algo, salt_hex, dk_hex = stored.split("$")
        if algo != "pbkdf2":
            return False
        salt = bytes.fromhex(salt_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKD)
        return hmac.compare_digest(dk.hex(), dk_hex)
    except (ValueError, AttributeError):
        return False


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def project_root() -> Path:
    return foundation_config.project_root()


def resolve_db_path() -> Path:
    cfg = foundation_config.load_config()
    rel = cfg.get("db_path") or "data/sgcc_foundation.sqlite"
    p = Path(rel)
    return project_root() / p if not p.is_absolute() else p


class Store:
    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else resolve_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connect()

    def _connect(self) -> None:
        raw = sqlite3.connect(str(self.db_path), timeout=10, check_same_thread=False)
        raw.row_factory = sqlite3.Row
        raw.execute("PRAGMA journal_mode=WAL")
        self.conn = _ThreadSafeConnection(raw)
        self._migrate()

    def close(self) -> None:
        self.conn.close()

    # -- migrations ---------------------------------------------------------
    def _migrate(self) -> None:
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            label TEXT NOT NULL,
            seat TEXT NOT NULL DEFAULT 'other'
        );
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role_id INTEGER NOT NULL,
            workspace_id TEXT,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (role_id) REFERENCES roles(id)
        );
        CREATE TABLE IF NOT EXISTS workspaces (
            id TEXT PRIMARY KEY,
            code TEXT UNIQUE NOT NULL,
            label TEXT NOT NULL,
            is_isolated INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workspace_id TEXT,
            key TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'draft',   -- draft, pending, approved, rejected, withdrawn
            current_stage TEXT NOT NULL DEFAULT 'review',
            requested_by INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            metadata TEXT NOT NULL DEFAULT '{}',
            FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE,
            FOREIGN KEY (requested_by) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor_id INTEGER,
            actor_username TEXT,
            action TEXT NOT NULL,
            target TEXT NOT NULL,
            details TEXT NOT NULL DEFAULT '{}',
            workspace_id TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (actor_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            expires_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_users_workspace ON users(workspace_id);
        CREATE INDEX IF NOT EXISTS idx_resources_workspace ON resources(workspace_id);
        CREATE INDEX IF NOT EXISTS idx_approvals_resource ON approvals (resource_id);
        """)
        # seed roles + workspaces (idempotent by code)
        self._seed_roles()
        self._seed_workspaces()
        # domain tables + seed are now handled by foundation/domains only;
        # core tables (roles/users/workspaces/resources/approvals/audit/sessions)
        # plus demo users are created above.
        self.seed_demo_users()
        # Domain tables (departments, employees, payroll, attendance, sites, AI Brain)
        # and M19 social-marketing tables are both created idempotently here.
        from .domains.migrate import create_domain_tables, create_m19_tables
        create_domain_tables(self.conn)
        create_m19_tables(self.conn)
        from .domains.ai_intelligence import ensure_ai_intelligence_schema
        ensure_ai_intelligence_schema(self.conn)
        self.conn.commit()

    def _seed_roles(self) -> None:
        for r in foundation_config.load_config()["roles"]:
            self.conn.execute(
                "INSERT OR IGNORE INTO roles (code,label,seat) VALUES (?,?,?)",
                (r["code"], r["label"], r.get("seat", "other")),
            )

    def _seed_workspaces(self) -> None:
        for w in foundation_config.load_config()["workspaces"]:
            self.conn.execute(
                "INSERT OR IGNORE INTO workspaces (id,code,label,is_isolated) VALUES (?,?,?,?)",
                (w["code"], w["code"], w["label"], 1 if w.get("is_isolated", True) else 0),
            )
        # sample resources per workspace for the isolated-data tests
        sample = {
            "SSC": [{"key": "workspace-sites", "name": "SSC Site Register", "desc": "SSC survey sites"}],
            "INFRA": [{"key": "contract-proposals", "name": "Contract Proposals", "desc": "INFRA contract proposals"}],
            "OTHER": [{"key": "reference-notes", "name": "Reference Notes", "desc": " OTHER reference notes"}],
        }
        for code, items in sample.items():
            wid = self.conn.execute(
                "SELECT id FROM workspaces WHERE code=?", (code,)).fetchone()
            if not wid:
                continue
            for it in items:
                self.conn.execute(
                    "INSERT OR IGNORE INTO resources (workspace_id,key,name,description) VALUES (?,?,?,?)",
                    (wid["id"], it["key"], it["name"], it["desc"]),
                )

    # -- convenience ---------------------------------------------------------
    def fetchall(self, sql: str, params=()) -> list[dict[str, Any]]:
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]

    def fetchone(self, sql: str, params=()) -> dict[str, Any] | None:
        row = self.conn.execute(sql, params).fetchone()
        return dict(row) if row else None

    def exec(self, sql: str, params=()) -> None:
        self.conn.execute(sql, params)
        self.conn.commit()

    def query(self, sql: str, params=()) -> list[dict[str, Any]]:
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]

    # -- seed demo users -----------------------------------------------------
    def seed_demo_users(self) -> None:
        cfg = foundation_config.load_config()
        if not cfg.get("seed_demo_users", True):
            return
        cur = self.conn.execute("SELECT COUNT(*) AS c FROM users")
        if cur.fetchone()["c"] == 0:
            for u in cfg.get("demo_users", []):
                self.conn.execute(
                    "INSERT INTO users (username,password_hash,name,role_id,workspace_id,active) "
                    "VALUES (?,?,?,?,?,1)",
                    (u["username"], _pbkdf2(u["password"]), u["name"],
                     self._role_id(u["role"]), u["workspace"]),
                )
            self.conn.commit()

    def _role_id(self, code: str) -> int:
        row = self.conn.execute("SELECT id FROM roles WHERE code=?", (code,)).fetchone()
        return row["id"] if row else 1

    # -- session helpers ------------------------------------------------------
    def create_session(self, user_id: int, expires_at: str | None = None) -> str:
        token = secrets.token_urlsafe(32)
        self.conn.execute(
            "INSERT INTO sessions (token,user_id,expires_at) VALUES (?, ?, ?)",
            (token, user_id, expires_at or (datetime.now(timezone.utc).timestamp() + 3600)),
        )
        self.conn.commit()
        return token

    def decode_session(self, token: str) -> dict[str, Any] | None:
        row = self.fetchone("SELECT s.*, u.username, u.name, u.role_id, r.code AS role, u.workspace_id, u.active "
                            "FROM sessions s JOIN users u ON u.id=s.user_id "
                            "LEFT JOIN roles r ON r.id=u.role_id WHERE s.token=?", (token,))
        if not row or not row["active"]:
            return None
        if not isinstance(row["expires_at"], str):
            expires = datetime.fromtimestamp(row["expires_at"], tz=timezone.utc).isoformat()
        else:
            expires = row["expires_at"]
        return {"token": row["token"], "user_id": row["user_id"], "username": row["username"],
                "name": row["name"], "role": row["role"], "workspace_id": row["workspace_id"],
                "active": row["active"], "expires_at": expires}

    # -- users -----------------------------------------------------------------
    def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        return self.fetchone("SELECT * FROM users WHERE username=?", (username,))

    def authenticate(self, username: str, password: str) -> dict[str, Any] | None:
        u = self.conn.execute(
            "SELECT u.*, r.code AS role FROM users u LEFT JOIN roles r ON r.id=u.role_id WHERE u.username=?", (username,)).fetchone()
        if not u or not u["active"]:
            return None
        if not _verify(password, u["password_hash"]):
            return None
        return {"id": u["id"], "username": u["username"], "name": u["name"],
                "role": u["role"], "workspace_id": u["workspace_id"], "active": u["active"]}

    def list_users(self) -> list[dict[str, Any]]:
        return self.fetchall("SELECT u.*, r.code AS role FROM users u LEFT JOIN roles r ON r.id=u.role_id")

    def get_user_by_id(self, user_id: int) -> dict[str, Any] | None:
        return self.fetchone(
            "SELECT u.*, r.code AS role FROM users u LEFT JOIN roles r ON r.id=u.role_id WHERE u.id=?", (user_id,))

    def create_user(self, username: str, password: str, name: str, role_id: int,
                    workspace_id: str, active: int = 1) -> dict[str, Any]:
        ph = _pbkdf2(password)
        cur = self.conn.execute(
            "INSERT INTO users (username,password_hash,name,role_id,workspace_id,active) "
            "VALUES (?,?,?,?,?,?)", (username, ph, name, role_id, workspace_id, active))
        self.conn.commit()
        return self.get_user_by_username(username)

    def update_user(self, user_id: int, username: str | None = None,
                    name: str | None = None, role_id: int | None = None,
                    workspace_id: str | None = None, active: int | None = None,
                    password: str | None = None) -> dict[str, Any] | None:
        sets: list[str] = []
        params: list[Any] = []
        if username is not None:
            sets.append("username=?"); params.append(username)
        if name is not None:
            sets.append("name=?"); params.append(name)
        if role_id is not None:
            sets.append("role_id=?"); params.append(role_id)
        if workspace_id is not None:
            sets.append("workspace_id=?"); params.append(workspace_id)
        if active is not None:
            sets.append("active=?"); params.append(active)
        if password is not None and password.strip():
            sets.append("password_hash=?"); params.append(_pbkdf2(password.strip()))
        if not sets:
            return self.get_user_by_id(user_id)
        params.append(user_id)
        self.conn.execute(
            "UPDATE users SET " + ", ".join(sets) + " WHERE id=?", params)
        self.conn.commit()
        return self.get_user_by_id(user_id)

    def deactivate_user(self, user_id: int, active: int = 0) -> dict[str, Any] | None:
        res = self.update_user(user_id, active=active)
        if active == 0:
            self.conn.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
            self.conn.commit()
        return res

    def activate_user(self, user_id: int) -> dict[str, Any] | None:
        return self.update_user(user_id, active=1)

    # -- roles ---------------------------------------------------------------
    def list_roles(self) -> list[dict[str, Any]]:
        return self.fetchall("SELECT * FROM roles ORDER BY code")

    # -- workspaces -----------------------------------------------------------
    def list_workspaces(self) -> list[dict[str, Any]]:
        return self.fetchall("SELECT * FROM workspaces ORDER BY code")

    def get_workspace(self, code: str) -> dict[str, Any] | None:
        return self.fetchone("SELECT * FROM workspaces WHERE code=?", (code,))

    # -- resources (workspace-scoped) -----------------------------------------
    def list_resources(self, workspace_id: str | None) -> list[dict[str, Any]]:
        if workspace_id is None:
            # Owner / system scope: no filter (owner sees all).
            return self.fetchall("SELECT * FROM resources ORDER BY workspace_id, key")
        return self.fetchall(
            "SELECT r.*, w.code AS workspace_code FROM resources r "
            "JOIN workspaces w ON w.id=r.workspace_id WHERE r.workspace_id=?", (workspace_id,))

    def get_resource(self, resource_id: int) -> dict[str, Any] | None:
        return self.fetchone("SELECT r.*, w.code AS workspace_code FROM resources r "
                             "JOIN workspaces w ON w.id=r.workspace_id WHERE r.id=?", (resource_id,))

    def create_resource(self, workspace_id: str, key: str, name: str, description: str = "") -> dict[str, Any]:
        cur = self.conn.execute(
            "INSERT INTO resources (workspace_id,key,name,description) VALUES (?,?,?,?)",
            (workspace_id, key, name, description))
        self.conn.commit()
        return self.get_resource(cur.lastrowid)

    # -- approvals (workspace-scoped) -----------------------------------------
    def list_approvals(self, workspace_id: str, status: str | None = None) -> list[dict[str, Any]]:
        sql = ("SELECT a.*, r.key AS resource_key, r.name AS resource_name, u.username AS requested_by_username "
               "FROM approvals a JOIN resources r ON r.id=a.resource_id "
               "JOIN users u ON u.id=a.requested_by "
               "WHERE r.workspace_id=?")
        params = [workspace_id]
        if status:
            sql += " AND a.status=?"
            params.append(status)
        sql += " ORDER BY a.created_at DESC"
        return self.fetchall(sql, params)

    def get_approval(self, approval_id: int) -> dict[str, Any] | None:
        return self.fetchone("SELECT a.*, r.key AS resource_key, r.name AS resource_name, "
                             "u.username AS requested_by_username FROM approvals a "
                             "JOIN resources r ON r.id=a.resource_id "
                             "JOIN users u ON u.id=a.requested_by WHERE a.id=?", (approval_id,))

    def create_approval(self, workspace_id: str, title: str, description: str,
                        requested_by: int, resource_key: str) -> dict[str, Any]:
        res = self.conn.execute(
            "SELECT id FROM resources WHERE workspace_id=? AND key=?", (workspace_id, resource_key)).fetchone()
        if not res:
            raise ValueError(f"resource {resource_key!r} not found in workspace {workspace_id}")
        cur = self.conn.execute(
            "INSERT INTO approvals (resource_id,title,description,requested_by,status,current_stage) "
            "VALUES (?,?,?,?, 'pending','review')",
            (res["id"], title, description, requested_by))
        self.conn.commit()
        return self.get_approval(cur.lastrowid)

    def transition_approval(self, approval_id: int, new_status: str, actor_user_id: int,
                            note: str = "") -> dict[str, Any]:
        require_approver(self, actor_user_id, approval_id)
        a = self.get_approval(approval_id)
        if not a:
            raise KeyError(f"approval {approval_id} not found")
        allowed = {"approved", "rejected", "withdrawn"}
        if new_status not in allowed:
            raise ValueError(f"bad status {new_status!r}")
        self.conn.execute(
            "UPDATE approvals SET status=?, current_stage='final', updated_at=? WHERE id=?",
            (new_status, now_iso(), approval_id))
        self.add_audit(actor_user_id, "approval:" + new_status, f"approval:{approval_id}",
                       {"note": note, "target": f"approval:{approval_id}", "from": a["status"]})
        return self.get_approval(approval_id)

    # -- audit -----------------------------------------------------------------
    def add_audit(self, actor_id: int | None, action: str, target: str,
                  details: dict | None = None, workspace_id: str | None = None) -> int:
        cur = self.conn.execute(
            "INSERT INTO audit_logs (actor_id,actor_username,action,target,details,workspace_id) "
            "VALUES (?,?,?,?,?,?)",
            (actor_id, actor_id and self.conn.execute("SELECT username FROM users WHERE id=?", (actor_id,)).fetchone()["username"],
             action, target, json_dumps(details), workspace_id))
        self.conn.commit()
        return cur.lastrowid

    def list_audit(self, workspace_id: str, limit: int = 0) -> list[dict[str, Any]]:
        sql = ("SELECT a.*, u.username AS actor_username FROM audit_logs a "
               "LEFT JOIN users u ON u.id=a.actor_id WHERE a.workspace_id=? "
               "ORDER BY a.created_at DESC")
        params = [workspace_id]
        if limit and limit > 0:
            sql += " LIMIT ?";
            params.append(limit)
        return self.fetchall(sql, params)

    # -- sites & projects -----------------------------------------------------
    def list_sites(self, workspace_id: str | None = None) -> list[dict[str, Any]]:
        sql = "SELECT * FROM sites"
        params: list[Any] = []
        if workspace_id:
            sql += " WHERE workspace_id=?"
            params.append(workspace_id)
        sql += " ORDER BY created_at DESC"
        return self.fetchall(sql, params)

    def create_site(self, workspace_id: str, name: str, code: str,
                    address: str = "", geofence_radius_m: float = 100.0,
                    field_policy_required: int = 0) -> dict[str, Any]:
        existing = self.fetchone("SELECT * FROM sites WHERE code=? AND workspace_id=?", (code, workspace_id))
        if existing:
            return existing
        cur = self.conn.execute(
            "INSERT INTO sites (workspace_id, name, code, address, geofence_radius_m, field_policy_required, created_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (workspace_id, name, code, address, float(geofence_radius_m), int(field_policy_required), now_iso())
        )
        self.conn.commit()
        return self.fetchone("SELECT * FROM sites WHERE id=?", (cur.lastrowid,))

    # -- clients ---------------------------------------------------------------
    def list_clients(self) -> list[dict[str, Any]]:
        return self.fetchall("SELECT * FROM social_client_profiles ORDER BY created_at DESC")

    def create_client(self, client_workspace_id: str, company_name: str,
                      service_package: str = "", contract_metadata: dict | None = None) -> dict[str, Any]:
        self.conn.execute(
            "INSERT INTO social_client_profiles (client_workspace_id, company_name, service_package, contract_metadata, created_at) "
            "VALUES (?,?,?,?,?)",
            (client_workspace_id, company_name, service_package, json_dumps(contract_metadata or {}), now_iso())
        )
        self.conn.commit()
        return self.fetchone("SELECT * FROM social_client_profiles WHERE client_workspace_id=?", (client_workspace_id,))

    # -- finance & vendors -----------------------------------------------------
    def list_vendors(self, workspace_id: str | None = None) -> list[dict[str, Any]]:
        sql = "SELECT * FROM expense_vendors"
        params: list[Any] = []
        if workspace_id:
            sql += " WHERE workspace_id=?"
            params.append(workspace_id)
        sql += " ORDER BY created_at DESC"
        return self.fetchall(sql, params)

    def create_vendor(self, workspace_id: str, name: str, category: str = "vendor", contact: str = "") -> dict[str, Any]:
        existing = self.fetchone("SELECT * FROM expense_vendors WHERE name=? AND workspace_id=?", (name, workspace_id))
        if existing:
            return existing
        cur = self.conn.execute(
            "INSERT INTO expense_vendors (workspace_id, name, category, contact, created_at) VALUES (?,?,?,?,?)",
            (workspace_id, name, category, contact, now_iso())
        )
        self.conn.commit()
        return self.fetchone("SELECT * FROM expense_vendors WHERE id=?", (cur.lastrowid,))

    def list_expense_claims(self, workspace_id: str | None = None) -> list[dict[str, Any]]:
        sql = "SELECT * FROM expense_claims"
        params: list[Any] = []
        if workspace_id:
            sql += " WHERE workspace_id=?"
            params.append(workspace_id)
        sql += " ORDER BY created_at DESC"
        return self.fetchall(sql, params)

    def create_expense_claim(self, workspace_id: str, employee_id: int, project_id: str,
                             category: str, amount: float, notes: str = "", receipt_url: str = "") -> dict[str, Any]:
        cur = self.conn.execute(
            "INSERT INTO expense_claims (workspace_id, employee_id, project_id, category, amount, currency, receipt_url, status, submitted_by, notes, submitted_at, created_at) "
            "VALUES (?,?,?,?,?, 'INR', ?, 'submitted', ?, ?, ?, ?)",
            (workspace_id, employee_id, project_id, category, float(amount), receipt_url, employee_id, notes, now_iso(), now_iso())
        )
        self.conn.commit()
        return self.fetchone("SELECT * FROM expense_claims WHERE id=?", (cur.lastrowid,))

    # -- leads sync & conversion -----------------------------------------------
    def sync_leads_from_csv(self, csv_path: str, workspace_id: str = "SSC") -> dict[str, int]:
        import csv
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        imported = 0
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                comp = (row.get("company") or "").strip()
                if not comp:
                    continue
                existing = self.fetchone("SELECT id FROM social_leads WHERE company=? AND workspace_id=?", (comp, workspace_id))
                if existing:
                    continue
                loc_parts = [row.get("city", "").strip(), row.get("state", "").strip()]
                loc = ", ".join(p for p in loc_parts if p)
                self.conn.execute(
                    "INSERT INTO social_leads (workspace_id, client_workspace_id, lead_name, company, phone, email, "
                    "location, platform, source_post, enquiry_text, service_interest, lead_priority, lead_status, "
                    "quotation_status, conversion_status, created_at, updated_at) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (workspace_id, None, comp, comp, row.get("phone", ""), row.get("email", ""),
                     loc, row.get("lead_source", "csv_import"), row.get("source_url", ""),
                     row.get("notes", ""), row.get("business_category", ""),
                     (row.get("priority") or "medium").lower(), "new", "none", "none",
                     now_iso(), now_iso())
                )
                imported += 1
        self.conn.commit()
        total = len(self.fetchall("SELECT id FROM social_leads WHERE workspace_id=?", (workspace_id,)))
        return {"imported": imported, "total": total}

    def create_lead(self, workspace_id: str, lead_name: str, company: str = "",
                    service_interest: str = "", location: str = "", phone: str = "",
                    priority: str = "medium", notes: str = "") -> dict[str, Any]:
        comp = company or lead_name
        cur = self.conn.execute(
            "INSERT INTO social_leads (workspace_id, client_workspace_id, lead_name, company, phone, email, "
            "location, platform, source_post, enquiry_text, service_interest, lead_priority, lead_status, "
            "quotation_status, conversion_status, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (workspace_id, None, lead_name, comp, phone, "",
             location, "direct", "", notes, service_interest,
             priority.lower(), "new", "none", "none",
             now_iso(), now_iso())
        )
        self.conn.commit()
        return self.fetchone("SELECT * FROM social_leads WHERE id=?", (cur.lastrowid,)) or {}

    def convert_lead(self, lead_id: int, workspace_id: str, actor_id: int, create_site: bool = True) -> dict[str, Any]:
        lead = self.fetchone("SELECT * FROM social_leads WHERE id=? AND workspace_id=?", (lead_id, workspace_id))
        if not lead:
            raise KeyError(f"lead {lead_id} not found in workspace {workspace_id}")
        client_code = f"CLT-{int(lead_id):03d}"
        comp_name = lead["company"] or lead["lead_name"] or f"Client {client_code}"

        client = self.fetchone("SELECT * FROM social_client_profiles WHERE client_workspace_id=?", (client_code,))
        if not client:
            meta = {
                "source_lead_id": lead["id"],
                "phone": lead["phone"],
                "email": lead["email"],
                "location": lead["location"]
            }
            client = self.create_client(client_code, comp_name, lead["service_interest"] or "Survey & Consultancy", meta)

        self.conn.execute(
            "UPDATE social_leads SET lead_status='won', conversion_status='converted', client_workspace_id=?, updated_at=? WHERE id=?",
            (client_code, now_iso(), lead_id)
        )
        self.conn.commit()

        site = None
        if create_site:
            site_code = f"SITE-CLT-{int(lead_id):02d}"
            site = self.fetchone("SELECT * FROM sites WHERE code=? AND workspace_id=?", (site_code, workspace_id))
            if not site:
                site_name = f"{comp_name} - {lead['service_interest'] or 'Survey Site'}"
                addr = lead["location"] or "Client Project Location"
                site = self.create_site(workspace_id, site_name, site_code, addr, 150.0, 1)

        self.add_audit(actor_id, "lead:convert", f"lead:{lead_id}",
                       {"client_code": client_code, "company": comp_name, "site_code": site["code"] if site else None},
                       workspace_id)
        updated_lead = self.fetchone("SELECT * FROM social_leads WHERE id=?", (lead_id,))
        return {"lead": updated_lead, "client": client, "site": site}

    # -- HRM: Employees -------------------------------------------------------
    def list_employees(self, workspace_id: str | None = None) -> list[dict[str, Any]]:
        sql = "SELECT * FROM employees"
        params: list[Any] = []
        if workspace_id:
            sql += " WHERE workspace_id=?"
            params.append(workspace_id)
        sql += " ORDER BY created_at DESC"
        return self.fetchall(sql, params)

    def create_employee(self, workspace_id: str, name: str, role: str = "Field Technician",
                        department: str = "Operations", email: str = "", phone: str = "",
                        designation: str = "", salary: float = 0.0) -> dict[str, Any]:
        import time as _time
        emp_id = f"EMP-{workspace_id[:3].upper()}-{int(_time.time() * 1000) % 100000:05d}"
        cur = self.conn.execute(
            "INSERT INTO employees (workspace_id, employee_id, name, designation, department_id, "
            "hire_date, resignation_date, status, email, phone, manager_id, created_at) "
            "VALUES (?,?,?,?,NULL,?,'',' active',?,?,NULL,?)",
            (workspace_id, emp_id, name, designation or role, now_iso()[:10],
             email, phone, now_iso())
        )
        self.conn.commit()
        return self.fetchone("SELECT * FROM employees WHERE id=?", (cur.lastrowid,)) or {}

    # -- HRM: Attendance ------------------------------------------------------
    def list_attendance(self, workspace_id: str | None = None) -> list[dict[str, Any]]:
        sql = ("SELECT a.*, e.name AS employee_name FROM attendance_logs a "
               "LEFT JOIN employees e ON e.id = a.employee_id")
        params: list[Any] = []
        if workspace_id:
            sql += " WHERE a.workspace_id=?"
            params.append(workspace_id)
        sql += " ORDER BY a.created_at DESC LIMIT 200"
        return self.fetchall(sql, params)

    def log_attendance(self, workspace_id: str, employee_id: int, event: str = "check_in",
                       lat: float = 0.0, lng: float = 0.0, notes: str = "") -> dict[str, Any]:
        ts = now_iso()
        # attendance_logs requires check_in, check_out, site_id (default 0)
        if event == "check_out":
            cur = self.conn.execute(
                "INSERT INTO attendance_logs (workspace_id, employee_id, site_id, check_in, check_out, "
                "gps_lat, gps_lng, geofence_passed, selfie_taken, status, notes, created_at) "
                "VALUES (?,?,0,?,?,?,?,0,0,'present',?,?)",
                (workspace_id, employee_id, ts, ts, lat, lng, notes, ts)
            )
        else:
            cur = self.conn.execute(
                "INSERT INTO attendance_logs (workspace_id, employee_id, site_id, check_in, check_out, "
                "gps_lat, gps_lng, geofence_passed, selfie_taken, status, notes, created_at) "
                "VALUES (?,?,0,?,'',?,?,0,0,'present',?,?)",
                (workspace_id, employee_id, ts, lat, lng, notes, ts)
            )
        self.conn.commit()
        return self.fetchone("SELECT * FROM attendance_logs WHERE id=?", (cur.lastrowid,)) or {}

    # -- HRM: Leaves ----------------------------------------------------------
    def list_leaves(self, workspace_id: str | None = None) -> list[dict[str, Any]]:
        # leaves table has no workspace_id column; join via employee_id
        sql = ("SELECT l.*, e.name AS employee_name, e.workspace_id FROM leaves l "
               "LEFT JOIN employees e ON e.id = l.employee_id")
        params: list[Any] = []
        if workspace_id:
            sql += " WHERE e.workspace_id=?"
            params.append(workspace_id)
        sql += " ORDER BY l.created_at DESC"
        return self.fetchall(sql, params)

    def create_leave(self, workspace_id: str, employee_id: int, leave_type: str,
                     from_date: str, to_date: str, reason: str = "") -> dict[str, Any]:
        # Calculate days (simple date diff approximation)
        try:
            from datetime import date
            d1 = date.fromisoformat(from_date)
            d2 = date.fromisoformat(to_date)
            days = max(1, (d2 - d1).days + 1)
        except Exception:
            days = 1
        cur = self.conn.execute(
            "INSERT INTO leaves (employee_id, type, start_date, end_date, days, status, approved_by, reason, created_at) "
            "VALUES (?,?,?,?,?,'applied',NULL,?,?)",
            (employee_id, leave_type, from_date, to_date, days, reason, now_iso())
        )
        self.conn.commit()
        return self.fetchone("SELECT * FROM leaves WHERE id=?", (cur.lastrowid,)) or {}

    # -- Business Operations (Estimates, Quotations, Work Orders, Invoices, Payments, P&L) --
    def create_estimate(self, workspace_id: str, data: dict[str, Any]) -> dict[str, Any]:
        from .domains import business_ops
        return business_ops.create_estimate(self.conn, workspace_id, data)

    def list_estimates(self, workspace_id: str, status: str | None = None) -> list[dict[str, Any]]:
        from .domains import business_ops
        return business_ops.list_estimates(self.conn, workspace_id, status)

    def get_estimate(self, estimate_id: int) -> dict[str, Any] | None:
        from .domains import business_ops
        return business_ops.get_estimate(self.conn, estimate_id)

    def update_estimate_status(self, estimate_id: int, status: str) -> dict[str, Any] | None:
        from .domains import business_ops
        return business_ops.update_estimate_status(self.conn, estimate_id, status)

    def create_quotation(self, workspace_id: str, data: dict[str, Any]) -> dict[str, Any]:
        from .domains import business_ops
        return business_ops.create_quotation(self.conn, workspace_id, data)

    def list_quotations(self, workspace_id: str, status: str | None = None) -> list[dict[str, Any]]:
        from .domains import business_ops
        return business_ops.list_quotations(self.conn, workspace_id, status)

    def get_quotation(self, quotation_id: int) -> dict[str, Any] | None:
        from .domains import business_ops
        return business_ops.get_quotation(self.conn, quotation_id)

    def update_quotation_status(self, quotation_id: int, status: str) -> dict[str, Any] | None:
        from .domains import business_ops
        return business_ops.update_quotation_status(self.conn, quotation_id, status)

    def create_work_order(self, workspace_id: str, data: dict[str, Any]) -> dict[str, Any]:
        from .domains import business_ops
        return business_ops.create_work_order(self.conn, workspace_id, data)

    def list_work_orders(self, workspace_id: str, status: str | None = None) -> list[dict[str, Any]]:
        from .domains import business_ops
        return business_ops.list_work_orders(self.conn, workspace_id, status)

    def get_work_order(self, work_order_id: int) -> dict[str, Any] | None:
        from .domains import business_ops
        return business_ops.get_work_order(self.conn, work_order_id)

    def update_work_order_status(self, work_order_id: int, status: str,
                                 field_qc_status: str | None = None,
                                 deliverables_status: str | None = None) -> dict[str, Any] | None:
        from .domains import business_ops
        return business_ops.update_work_order_status(self.conn, work_order_id, status, field_qc_status, deliverables_status)

    def create_invoice(self, workspace_id: str, data: dict[str, Any]) -> dict[str, Any]:
        from .domains import business_ops
        return business_ops.create_invoice(self.conn, workspace_id, data)

    def list_invoices(self, workspace_id: str, status: str | None = None) -> list[dict[str, Any]]:
        from .domains import business_ops
        return business_ops.list_invoices(self.conn, workspace_id, status)

    def get_invoice(self, invoice_id: int) -> dict[str, Any] | None:
        from .domains import business_ops
        return business_ops.get_invoice(self.conn, invoice_id)

    def record_payment(self, workspace_id: str, invoice_id: int, data: dict[str, Any]) -> dict[str, Any]:
        from .domains import business_ops
        return business_ops.record_payment(self.conn, workspace_id, invoice_id, data)

    def list_payments(self, workspace_id: str, invoice_id: int | None = None) -> list[dict[str, Any]]:
        from .domains import business_ops
        return business_ops.list_payments(self.conn, workspace_id, invoice_id)

    def get_profit_loss_summary(self, workspace_id: str) -> dict[str, Any]:
        from .domains import business_ops
        return business_ops.get_profit_loss_summary(self.conn, workspace_id)


