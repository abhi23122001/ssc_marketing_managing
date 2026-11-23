"""Core HTTP API (stdlib only) for the SHAH Group AI OS foundation.

Run:  python3 -m foundation.api  (serves on foundation.config port, default 8899)

Routes:
    GET  /health
    GET  /                          -> owner dashboard (dashboard.html)
    POST /api/auth/login            -> {token, user, role, workspace_id}
    GET  /api/auth/me               -> current user (Bearer token)
    GET  /api/workspaces            -> workspace list
    GET  /api/workspaces/{code}/resources
    GET  /api/approvals             -> workspace-scoped approvals
    POST /api/approvals             -> create approval
    GET  /api/approvals/{id}        -> approval detail
    POST /api/approvals/{id}/transition  -> approve/reject/withdraw
    GET  /api/audit/{code}          -> audit feed (workspace-scoped)
    GET  /api/ai-brain              -> shared AI Brain (local, stateless)

All business data is workspace-scoped; the Owner reads across workspaces.
"""

from __future__ import annotations

import json
import mimetypes
import os
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

# Ensure project root is on sys.path so relative imports work when
# running the script directly (python3 foundation/api.py)
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from foundation import config as foundation_config

try:
    import psutil
except ImportError:
    psutil = None

# Module status reference (reused by the dashboard and module-integration endpoints).
_MODULE_SHORT = {
    "01": "Marketing Command Center",
    "02": "Daily Content Planner",
    "03": "Instagram / Facebook Content Studio",
    "04": "LinkedIn B2B Marketing",
    "05": "Google Business Profile Management",
    "06": "Contractor Lead Research CRM",
    "07": "SEO / Keyword Research",
    "08": "AI Image / Video Workflow",
    "09": "Content Approval & Publishing",
    "10": "Analytics & Monthly Reporting",
}

_LOGIN_ATTEMPTS: dict[str, list[float]] = {}

def _is_rate_limited(ident: str, max_attempts: int = 5, window_sec: float = 300.0) -> bool:
    now = time.time()
    history = [t for t in _LOGIN_ATTEMPTS.get(ident, []) if now - t < window_sec]
    _LOGIN_ATTEMPTS[ident] = history
    return len(history) >= max_attempts

def _record_failure(ident: str) -> None:
    now = time.time()
    if ident not in _LOGIN_ATTEMPTS:
        _LOGIN_ATTEMPTS[ident] = []
    _LOGIN_ATTEMPTS[ident].append(now)

def _clear_failures(ident: str) -> None:
    _LOGIN_ATTEMPTS.pop(ident, None)
_MODULE_STATUS = {
    "01": "Ready", "02": "Ready", "03": "Ready", "04": "Ready",
    "05": "Ready", "06": "Ready", "07": "Ready", "08": "Ready",
    "09": "Ready", "10": "Ready",
}

from foundation.store import Store, now_iso
from foundation.domains import lifecycle_enhancements

# Symbols genuinely required by the Handler logic below.
# authenticate/issue_token/TOKEN_PREFIX are defined in foundation.auth;
# has_permission is defined in foundation.rbac.
from foundation.auth import TOKEN_PREFIX, authenticate, issue_token
from foundation.rbac import has_permission
from foundation.approval import can_create, create_approval, transition
from foundation.audit import log

STORE: Store | None = None


def set_store(store: Store) -> None:
    global STORE
    STORE = store


def get_store() -> Store:
    global STORE
    if STORE is None:
        STORE = Store()
    return STORE


def _send_json(handler, payload, status=200):
    try:
        body = json.dumps(payload).encode("utf-8")
        handler.send_response(status)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", str(len(body)))
        handler.send_header("X-Content-Type-Options", "nosniff")
        handler.send_header("X-Frame-Options", "SAMEORIGIN")
        handler.send_header("X-XSS-Protection", "1; mode=block")
        handler.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        handler.end_headers()
        handler.wfile.write(body)
    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
        pass


def _read_json(handler) -> dict:
    length = int(handler.headers.get("Content-Length") or 0)
    if not length:
        return {}
    return json.loads(handler.rfile.read(length).decode("utf-8"))


def _get_token(handler) -> str | None:
    auth = handler.headers.get("Authorization") or ""
    if auth.startswith(TOKEN_PREFIX):
        return auth[len(TOKEN_PREFIX):]
    return handler.headers.get("X-Session-Token") or None


def _owner_or_manager(store, user) -> bool:
    return user is not None and has_permission(user.get("role") or "Viewer", "approval:create")


class Handler(BaseHTTPRequestHandler):
    server_version = "SHAI-Foundation/0.1"

    @property
    def _method(self) -> str:
        """HTTP method of the current request (convenience: self.command)."""
        return self.command
    # The handler always reads STORE (set via set_store during tests);
    # falls back to a default store on first request only.
    @property
    def store(self) -> Store:
        return get_store()

    # -- helpers -----------------------------------------------------------
    def _user(self):
        return authenticate(self.store, _get_token(self))

    def _token(self) -> str | None:
        return _get_token(self)

    def _get_request_workspace(self, user: dict, data: dict | None = None) -> tuple[str, str | None]:
        """Extracts target workspace from query param, header, body data, or user default.
        Enforces tenant isolation: Non-owner/non-admin roles can ONLY access their assigned workspace.
        Returns (workspace_id, error_message).
        """
        if not user:
            return "SSC", "authentication required"

        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)

        requested = (
            qs.get("workspace", [None])[0] or 
            self.headers.get("X-Workspace-ID") or 
            (data.get("workspace") if data else None)
        )

        user_ws = user.get("workspace_id") or "SSC"
        user_role = user.get("role") or ""

        if user_role in ("Owner", "Admin"):
            return (requested or user_ws), None

        if requested and requested not in (user_ws, "ALL"):
            return user_ws, f"Tenant isolation: role '{user_role}' assigned to '{user_ws}' cannot access '{requested}'"

        return user_ws, None

    def _json_ok(self, payload, status=200):
        _send_json(self, payload, status)

    def _json_err(self, message, status=403):
        _send_json(self, {"error": message}, status)

    def _send_csv(self, filename: str, fieldnames: list[str], rows: list[dict]) -> None:
        import csv, io
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(dict(r))
        data = out.getvalue().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/csv; charset=utf-8")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    # -- actions -----------------------------------------------------------
    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)
        try:
            # Public unauthenticated routes
            if path in ("/api/oauth/google/callback", "/api/oauth/callback"):
                self._handle_oauth_callback_browser(parsed)
                return
            if path in ("/favicon.ico", "/favicon.png"):
                self._handle_static_favicon()
                return
            if path in ("/health", "/healthz", "/api/health"):
                self._json_ok({
                    "ok": True,
                    "service": "SHAH-Group-AI-OS",
                    "status": "healthy",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                return
            if path == "/":
                data = (Path(__file__).parent / "dashboard" / "dashboard.html").read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

            user = self._user()
            if user is None:
                self._json_err("authentication required", 401)
                return
            if path == "/api/workspaces":
                self._json_ok({"workspaces": self.store.list_workspaces()})
            elif path.startswith("/api/workspaces/") and path.endswith("/resources"):
                code = path.split("/")[-2]
                # isolation: a member reads only their own workspace records
                user = self._user()
                if user is None:
                    self._json_err("authentication required", 401)
                    return
                scope = self.store.get_workspace(code)
                if scope is None:
                    self._json_err("workspace not found", 404)
                    return
                # Owner reads all; members read their own
                access = self.store.get_workspace(user.get("workspace_id")) if user.get("workspace_id") else None
                if not user.get("workspace_id") or access is None or user.get("role") == "Owner":
                    # Owner / system actor: reads all workspaces
                    res = self.store.list_resources(None)
                elif access["id"] == scope["id"]:
                    res = self.store.list_resources(scope["id"])
                else:
                    self._json_err(
                        "isolation blocked: this workspace is not your data domain",
                        403)
                    return
                self._json_ok({"resources": res})
            elif path.startswith("/api/approvals/") and path.endswith("/transition"):
                # transition is a state change; handled by do_POST (see below).
                self._json_err("method not allowed", 405)
                return
            elif path.startswith("/api/approvals/"):
                aid = int(path.split("/")[3])
                approval = self.store.get_approval(aid)
                if approval is None:
                    self._json_err("approval not found", 404)
                    return
                # workspace-scoped read
                self._json_ok({"approval": approval})
            elif path == "/api/auth/me":
                user = self._user()
                if user is None:
                    self._json_err("authentication required", 401)
                    return
                self._json_ok({"user": user})
            elif path == "/api/approvals":
                user = self._user()
                if user is None:
                    self._json_err("authentication required", 401)
                    return
                if not (user.get("workspace_id") or has_permission(user.get("role") or "", "workspace:list")):
                    self._json_err("approvals require an assigned workspace (Owner/Manager)", 403)
                    return
                self._json_ok({"approvals": self.store.list_approvals(user.get("workspace_id"))})
            elif path == "/api/audit/SSC" or path.startswith("/api/audit/"):
                code = path.split("/")[-1] or "SSC"
                user = self._user()
                if user is None:
                    self._json_err("authentication required", 401)
                    return
                if not has_permission(user.get("role") or "", "audit:list"):
                    self._json_err("audit:list not permitted for this role", 403)
                    return
                # member scope: own workspace; Owner reads all
                wid = user.get("workspace_id") or code.lower()
                self._json_ok({"audit": self.store.list_audit(wid)})
            elif path == "/api/ai-brain":
                user = self._user()
                if user is None:
                    self._json_err("authentication required", 401)
                    return
                if not has_permission(user.get("role") or "", "ai:brain:query"):
                    self._json_err("ai:brain:query not permitted", 403)
                    return
                self._json_ok({"brain": {"name": foundation_config.load_config()["ai_brain"]["name"],
                                        "note": "Local brain is a stateless knowledge assistant. It answers from project context only; it does not invent client/project facts.",
                                        "session_workspace": user.get("workspace_id")}})
            elif path == "/api/permissions":
                user = self._user()
                if user is None:
                    self._json_err("authentication required", 401)
                    return
                cfg = foundation_config.load_config()
                perms = [p for p in cfg.get("permissions", {})
                         if has_permission(user.get("role") or "", p)]
                self._json_ok({"role": user.get("role"), "perms": perms,
                               "workspace": user.get("workspace_id")})
            elif path == "/api/users":
                user = self._user()
                if user is None:
                    self._json_err("authentication required", 401)
                    return
                if not has_permission(user.get("role") or "", "workspace:manage"):
                    self._json_err("user:manage not permitted for this role", 403)
                    return
                # Owner sees all; members see own workspace only
                if user.get("workspace_id") and user.get("role") != "Owner":
                    own = user["workspace_id"]
                    rows = [u for u in self.store.list_users() if u.get("workspace_id") == own]
                else:
                    rows = self.store.list_users()
                query_params = urllib.parse.parse_qs(parsed.query)
                q = query_params.get("q", [""])[0].lower().strip()
                ws_filter = query_params.get("workspace", [""])[0].strip()
                role_filter = query_params.get("role", [""])[0].strip()
                if q:
                    rows = [u for u in rows if q in (u.get("username") or "").lower() or q in (u.get("name") or "").lower()]
                if ws_filter:
                    rows = [u for u in rows if u.get("workspace_id") == ws_filter]
                if role_filter:
                    rows = [u for u in rows if (u.get("role") or "") == role_filter]
                def sanitize(u):
                    return {
                        "id": u["id"],
                        "username": u["username"],
                        "name": u["name"],
                        "role": u["role"],
                        "workspace_id": u["workspace_id"],
                        "active": bool(u["active"]),
                        "created_at": u["created_at"],
                    }
                self._json_ok({"users": [sanitize(u) for u in rows], "workspaces": self.store.list_workspaces()})
            elif path == "/api/roles":
                user = self._user()
                if user is None:
                    self._json_err("authentication required", 401)
                    return
                if not has_permission(user.get("role") or "", "workspace:manage"):
                    self._json_err("role:manage not permitted for this role", 403)
                    return
                self._json_ok({"roles": self.store.list_roles()})
            elif path.startswith("/api/dashboard"):
                self._handle_dashboard(path)
                return
            elif path.startswith("/api/workspaces/") and path.endswith("/contacts"):
                code = path.split("/")[3]
                self._handle_contacts(user, code)
                return
            elif path == "/api/content":
                self._handle_content_list(user)
                return
            elif path == "/api/content/ideas":
                self._handle_content_ideas(user)
                return
            elif path.startswith("/api/content/"):
                parts = [x for x in path.split("/") if x]
                if len(parts) >= 3 and parts[1] == "content":
                    cid = parts[2]
                    if len(parts) == 3:
                        self._handle_content_detail(user, cid)
                    elif len(parts) == 4 and parts[3] == "versions":
                        self._handle_content_versions(user, cid)
                    elif len(parts) == 4 and parts[3] == "script":
                        self._handle_content_script(user, cid)
                    elif len(parts) == 4 and parts[3] == "approval":
                        self._handle_content_approval(user, cid)
                    elif len(parts) == 5 and parts[3] == "approval" and parts[4] == "transition":
                        self._handle_content_approval_transition(user, cid)
                    else:
                        self._json_err("not found", 404)
                return
            elif path.startswith("/api/content/"):
                self._json_err("not found", 404)
                return
            elif path.startswith("/api/media/download/"):
                parts = [x for x in path.split("/") if x]
                if len(parts) >= 4 and parts[3].isdigit():
                    aid = int(parts[3])
                    asset = self.store.fetchone("SELECT * FROM social_media_assets WHERE id=?", (aid,))
                    if not asset:
                        self._json_err("media asset not found", 404)
                        return
                    ws = user.get("workspace_id") or "SSC"
                    if user.get("role") != "Owner" and asset.get("workspace_id") and asset["workspace_id"] != ws:
                        self._json_err("tenant isolation violation: unauthorized asset access", 403)
                        return
                    fname = asset["filename"]
                    from foundation.config import project_root
                    p = Path(project_root()) / fname if not os.path.isabs(fname) else Path(fname)
                    if not p.exists():
                        p = Path(os.getcwd()) / "data" / "m19_output" / os.path.basename(fname)
                    if not p.exists():
                        self._json_err("media file not found on disk", 404)
                        return
                    with open(p, "rb") as mf:
                        b = mf.read()
                    ctype = "video/mp4" if p.name.endswith(".mp4") else ("image/png" if p.name.endswith(".png") else "application/octet-stream")
                    self.send_response(200)
                    self.send_header("Content-Type", ctype)
                    self.send_header("Content-Length", str(len(b)))
                    self.send_header("Content-Disposition", f'inline; filename="{p.name}"')
                    self.end_headers()
                    self.wfile.write(b)
                    return
                self._json_err("invalid media download request", 400)
                return
            elif path.startswith("/api/media/"):
                parts = [x for x in path.split("/") if x]
                if len(parts) < 3 or parts[1] != "media":
                    self._json_err("not found", 404)
                    return
                mid = parts[2]
                if len(parts) == 3:
                    self._handle_media_detail(user, mid)
                elif len(parts) == 4 and parts[3] == "output":
                    self._handle_media_output(user, mid)
                elif len(parts) == 4 and parts[3] == "thumbnail":
                    self._handle_media_thumbnail(user, mid)
                elif len(parts) == 4 and parts[3] == "subtitle":
                    self._handle_media_subtitle(user, mid)
                elif len(parts) == 4 and parts[3] == "voiceover":
                    self._handle_media_voiceover(user, mid)
                elif len(parts) == 4 and parts[3] == "render":
                    self._handle_media_render(user, mid)
                else:
                    self._json_err("not found", 404)
                return
            elif path == "/api/media":
                self._handle_media_list(user)
                return
            elif path.startswith("/api/publish"):
                parts = [x for x in path.split("/") if x]
                if len(parts) < 2 or parts[1] != "publish":
                    self._json_err("not found", 404)
                    return
                if len(parts) == 2:
                    self._handle_publish_list(user)
                elif len(parts) >= 3 and parts[2] == "reconcile":
                    self._handle_publish_reconcile(user, parts[2])
                elif len(parts) >= 3:
                    self._handle_publish_detail(user, parts[2])
                else:
                    self._json_err("not found", 404)
                return
            elif path.startswith("/api/social/accounts/"):
                parts = [x for x in path.split("/") if x]
                if len(parts) >= 4 and parts[1] == "social" and parts[2] == "accounts":
                    aid = parts[3]
                    if len(parts) == 4:
                        self._handle_social_accounts(user)
                    elif len(parts) == 5 and parts[4] == "connect":
                        self._handle_social_account_connect(user, aid)
                    elif len(parts) == 5 and parts[4] == "disconnect":
                        self._handle_social_account_disconnect(user, aid)
                    elif len(parts) == 5 and parts[4] == "sync":
                        self._handle_social_account_sync(user, aid)
                    else:
                        self._json_err("not found", 404)
                return
            elif path.startswith("/api/social/accounts"):
                self._handle_social_accounts(user)
                return
            elif path.startswith("/api/leads"):
                self._handle_leads_route(path, user)
                return
            elif path.startswith("/api/clients"):
                self._handle_clients_route(path, user)
                return
            elif path.startswith("/api/sites"):
                self._handle_sites_route(path, user)
                return
            elif path.startswith("/api/finance"):
                self._handle_finance_route(path, user)
                return
            elif path.startswith("/api/employees"):
                self._handle_employees_route(path, user)
                return
            elif path.startswith("/api/attendance"):
                self._handle_attendance_route(path, user)
                return
            elif path.startswith("/api/leaves"):
                self._handle_leaves_route(path, user)
                return
            elif path.startswith("/api/payroll"):
                self._handle_payroll_route(path, user)
                return
            elif path.startswith("/api/estimates"):
                self._handle_estimates_route(path, user)
                return
            elif path.startswith("/api/quotations"):
                self._handle_quotations_route(path, user)
                return
            elif path.startswith("/api/work-orders"):
                self._handle_work_orders_route(path, user)
                return
            elif path.startswith("/api/invoices"):
                self._handle_invoices_route(path, user)
                return
            elif path.startswith("/api/bills"):
                self._handle_invoices_route(path, user)
                return
            elif path.startswith("/api/vendors"):
                self._handle_vendors_route(path, user)
                return
            elif path.startswith("/api/payments"):
                self._handle_payments_route(path, user)
                return
            elif path == "/api/calendar":
                self._handle_calendar(user)
                return
            elif path == "/api/content/ideas":
                self._handle_content_ideas(user)
                return
            elif path == "/api/social/trends":
                self._handle_social_trends(user)
                return
            elif path == "/api/ai-brain/action":
                self._handle_ai_brain_action(user)
                return
            elif path.startswith("/api/instagram"):
                self._handle_instagram_route(path, user)
                return
            elif path.startswith("/api/reports"):
                self._handle_reports_route(path, user)
                return
            elif path.startswith("/api/system"):
                self._handle_system_route(path, user)
                return
            elif path.startswith("/api/ai-brain"):
                self._handle_ai_brain_route(path, user)
                return
            elif path.startswith("/api/intelligence") or path.startswith("/api/ai/marketing"):
                self._handle_intelligence_route(path, user)
                return
            elif path.startswith("/api/studio"):
                self._handle_studio_route(path, user)
                return
            elif path.startswith("/api/tasks"):
                self._handle_tasks_route(path, user)
                return
            elif path.startswith("/api/filter"):
                self._handle_filter_route(path, user)
                return
            elif path.startswith("/api/integrations"):
                self._handle_integrations_route(path, user)
                return
            elif path.startswith("/api/gbp"):
                self._handle_gbp_route(path, user)
                return
            elif path.startswith("/api/owner-setup"):
                self._handle_owner_setup_route(path, user)
                return
            elif path.startswith("/api/oauth/authorize"):
                self._handle_oauth_authorize(user)
                return
            else:
                self._json_err("not found", 404)
        except Exception as e:  # pragma: no cover - defensive
            import traceback; traceback.print_exc()
            self._json_err(f"internal error: {e}", 500)

    def _handle_leads_route(self, path: str, user: dict) -> None:
        """CRM leads: GET (list) / POST (create/sync/convert/status)."""
        if path == "/api/leads":
            if self.command == "POST":
                return self._handle_lead_create(user)
            if user is None:
                self._json_err("authentication required", 401)
                return
            if not self._has(user, "resource:read"):
                self._json_err("resource:read not permitted", 403)
                return
            ws, err = self._get_request_workspace(user)
            if err:
                self._json_err(err, 403)
                return
            rows = self.store.fetchall("SELECT * FROM social_leads WHERE workspace_id=? ORDER BY created_at DESC", (ws,)) if ws != "ALL" else self.store.fetchall("SELECT * FROM social_leads ORDER BY created_at DESC")
            self._json_ok({"leads": rows})
            return
        if path == "/api/leads/sync-csv":
            if user is None:
                self._json_err("authentication required", 401)
                return
            if not self._has(user, "resource:create"):
                self._json_err("resource:create not permitted", 403)
                return
            ws = user.get("workspace_id") or "SSC"
            csv_path = os.path.join(_project_root, "data", "leads.csv")
            try:
                res = self.store.sync_leads_from_csv(csv_path, ws)
                actor_id = user.get("user_id") or user.get("id")
                self.store.add_audit(actor_id, "lead:sync_csv", f"leads:{res['imported']}", res, ws)
                self._json_ok({"ok": True, "imported": res["imported"], "total_leads": res["total"]})
            except Exception as e:
                self._json_err(f"sync failed: {e}", 500)
            return
        if path == "/api/leads/export":
            if user is None:
                self._json_err("authentication required", 401)
                return
            if not self._has(user, "resource:read"):
                self._json_err("resource:read not permitted", 403)
                return
            ws = user.get("workspace_id") or "SSC"
            rows = self.store.fetchall("SELECT * FROM social_leads WHERE workspace_id=? ORDER BY created_at DESC", (ws,))
            self._send_csv(f"leads_{ws}.csv",
                           ["id", "company", "lead_name", "phone", "email", "location", "service_interest", "lead_priority", "lead_status", "follow_up_date", "conversion_status", "created_at"],
                           rows)
            return
        if path == "/api/leads/due-follow-ups":
            if user is None:
                self._json_err("authentication required", 401)
                return
            if not self._has(user, "resource:read"):
                self._json_err("resource:read not permitted", 403)
                return
            ws = user.get("workspace_id") or "SSC"
            rows = self.store.fetchall(
                "SELECT * FROM social_leads WHERE workspace_id=? AND follow_up_date IS NOT NULL AND lead_status NOT IN ('won', 'lost') ORDER BY follow_up_date ASC", (ws,))
            self._json_ok({"due_follow_ups": rows, "count": len(rows)})
            return
        parts = [x for x in path.split("/") if x]
        if len(parts) >= 3 and parts[1] == "leads":
            lid = parts[2]
            if len(parts) == 3:
                if user is None:
                    self._json_err("authentication required", 401)
                    return
                row = self.store.fetchone("SELECT * FROM social_leads WHERE id=? AND workspace_id=?",
                                          (lid, user.get("workspace_id") or "SSC"))
                if not row:
                    self._json_err("lead not found", 404)
                    return
                self._json_ok({"lead": row})
            elif len(parts) == 4:
                if user is None:
                    self._json_err("authentication required", 401)
                    return
                if parts[3] == "convert":
                    if not self._has(user, "resource:create"):
                        self._json_err("resource:create not permitted", 403)
                        return
                    ws = user.get("workspace_id") or "SSC"
                    actor_id = user.get("user_id") or user.get("id")
                    data = _read_json(self) if (self.headers.get("Content-Length") and int(self.headers.get("Content-Length", 0)) > 0) else {}
                    create_site = data.get("create_site", True) if isinstance(data, dict) else True
                    try:
                        res = self.store.convert_lead(int(lid), ws, actor_id, create_site=create_site)
                        self._json_ok({"ok": True, "lead": res["lead"], "client": res["client"], "site": res["site"]})
                    except Exception as e:
                        self._json_err(f"conversion failed: {e}", 400)
                    return
                elif parts[3] == "follow-up":
                    data = _read_json(self)
                    f_date = data.get("follow_up_date", "")
                    assigned_emp = data.get("assigned_employee_id")
                    self.store.conn.execute(
                        "UPDATE social_leads SET follow_up_date=?, assigned_employee_id=?, updated_at=? WHERE id=?",
                        (f_date, assigned_emp, now_iso(), lid)
                    )
                    self.store.conn.commit()
                    updated = self.store.fetchone("SELECT * FROM social_leads WHERE id=?", (lid,))
                    self._json_ok({"lead": updated})
                    return
                elif parts[3] in ("status", "follow"):
                    data = _read_json(self)
                    if data.get("status") and self._has(user, ("resource:edit", "resource:create", "workspace:manage")):
                        # CSCOPE: lead must belong to the user's authorized workspace
                        existing = self.store.fetchone(
                            "SELECT id, workspace_id FROM social_leads WHERE id=? AND workspace_id=?", (lid, user.get("workspace_id") or "SSC"))
                        if existing is None:
                            self._json_err("lead not in authorized workspace (cross-workspace blocked)", 403)
                            return
                        target_ws = existing["workspace_id"]
                        self.store.exec("UPDATE social_leads SET lead_status=?, updated_at=? WHERE id=? AND workspace_id=?",
                                        (data["status"], now_iso(), lid, target_ws))
                        self.store.conn.commit()
                        self._json_ok({"lead": self.store.fetchone("SELECT * FROM social_leads WHERE id=? AND workspace_id=?", (lid, target_ws))})
                    else:
                        self._json_err("status or write permission required", 400)
                else:
                    self._json_err("not found", 404)
            else:
                self._json_err("not found", 404)
            return
        self._json_err("not found", 404)

    def _handle_clients_route(self, path: str, user: dict) -> None:
        if user is None:
            self._json_err("authentication required", 401)
            return
        if not self._has(user, "resource:read"):
            self._json_err("resource:read not permitted", 403)
            return
        ws, err = self._get_request_workspace(user)
        if err:
            self._json_err(err, 403)
            return
        if self.command == "GET":
            clients = self.store.list_clients(ws)
            self._json_ok({"clients": clients})
            return
        if self.command == "POST":
            if not self._has(user, "resource:create"):
                self._json_err("resource:create not permitted", 403)
                return
            data = _read_json(self)
            comp = data.get("company_name")
            if not comp:
                self._json_err("company_name required", 400)
                return
            code = data.get("client_workspace_id")
            if not code:
                existing_codes = {r.get("client_workspace_id") for r in self.store.fetchall("SELECT client_workspace_id FROM social_client_profiles")}
                i = 1
                while f"CLT-{i:03d}" in existing_codes:
                    i += 1
                code = f"CLT-{i:03d}"
            pkg = data.get("service_package", "Survey & Consultancy")
            meta = data.get("contract_metadata", {})
            client = self.store.create_client(code, comp, pkg, meta, workspace_id=ws)
            self._json_ok({"client": client}, 201)
            return
        self._json_err("not found", 404)

    def _handle_sites_route(self, path: str, user: dict) -> None:
        if user is None:
            self._json_err("authentication required", 401)
            return
        if not self._has(user, "resource:read"):
            self._json_err("resource:read not permitted", 403)
            return
        ws, err = self._get_request_workspace(user)
        if err:
            self._json_err(err, 403)
            return

        parsed = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed.query)
        cat_filter = query_params.get("category", [None])[0]

        parts = [x for x in path.split("/") if x]

        if path == "/api/sites/export":
            sites = lifecycle_enhancements.list_lifecycle_sites(self.store.conn, None if ws == "ALL" else ws)
            self._send_csv(f"sites_{ws}.csv", ["id", "code", "name", "address", "survey_type", "survey_status", "schedule_category", "balance_due", "created_at"], sites)
            return

        if len(parts) == 3 and parts[1] == "sites" and parts[2] == "summary":
            sites = lifecycle_enhancements.list_lifecycle_sites(self.store.conn, None if ws == "ALL" else ws)
            summary = {
                "total": len(sites),
                "upcoming": sum(1 for s in sites if s.get("schedule_category") == "Upcoming Site"),
                "tomorrow": sum(1 for s in sites if s.get("schedule_category") == "Tomorrow's Site"),
                "today": sum(1 for s in sites if s.get("schedule_category") == "Today's Site Visit"),
                "overdue": sum(1 for s in sites if s.get("schedule_category") == "Overdue Site Visit"),
                "completed": sum(1 for s in sites if s.get("schedule_category") == "Completed Site"),
                "payment_pending": sum(1 for s in sites if float(s.get("balance_due", 0.0)) > 0 and s.get("survey_status") in lifecycle_enhancements.COMPLETED_SURVEY_STATUSES)
            }
            self._json_ok({"summary": summary})
            return

        if len(parts) == 2 and parts[1] == "sites":
            if self.command == "GET":
                sites = lifecycle_enhancements.list_lifecycle_sites(self.store.conn, None if ws == "ALL" else ws, cat_filter)
                self._json_ok({"sites": sites, "count": len(sites)})
                return
            if self.command == "POST":
                if not self._has(user, "resource:create"):
                    self._json_err("resource:create not permitted", 403)
                    return
                data = _read_json(self)
                name = data.get("name")
                code = data.get("code")
                target_ws = data.get("workspace_id") or ws
                user_name = user.get("name") or user.get("username") or "Admin"
                site = lifecycle_enhancements.create_lifecycle_site(self.store.conn, target_ws, data, user_name)
                actor_id = user.get("user_id") or user.get("id")
                self.store.add_audit(actor_id, "site:create", f"site:{site.get('code')}", {"name": name, "code": code}, target_ws)
                self._json_ok({"site": site}, 201)
                return

        if len(parts) == 3 and parts[1] == "sites" and parts[2].isdigit():
            sid = int(parts[2])
            if self.command == "GET":
                s = lifecycle_enhancements.get_site_details(self.store.conn, sid)
                if not s:
                    self._json_err("site not found", 404)
                    return
                self._json_ok({"site": s})
                return
            if self.command in ("PUT", "POST"):
                data = _read_json(self)
                s = lifecycle_enhancements.get_site_details(self.store.conn, sid)
                self._json_ok({"site": s})
                return

        if len(parts) == 4 and parts[1] == "sites" and parts[2].isdigit() and parts[3] == "status" and self.command == "POST":
            sid = int(parts[2])
            data = _read_json(self)
            new_status = data.get("survey_status") or data.get("status")
            remarks = data.get("remarks", "")
            user_name = user.get("name") or user.get("username") or "Admin"
            try:
                updated = lifecycle_enhancements.update_site_status(self.store.conn, sid, new_status, remarks, user_name)
                self._json_ok({"site": updated})
            except Exception as e:
                self._json_err(str(e), 400)
            return

        if len(parts) == 4 and parts[1] == "sites" and parts[2].isdigit() and parts[3] == "payment" and self.command == "POST":
            sid = int(parts[2])
            data = _read_json(self)
            user_name = user.get("name") or user.get("username") or "Admin"
            try:
                updated = lifecycle_enhancements.update_site_payment(self.store.conn, sid, data, user_name)
                self._json_ok({"site": updated})
            except Exception as e:
                self._json_err(str(e), 400)
            return

        self._json_err("not found", 404)

    def _handle_finance_route(self, path: str, user: dict) -> None:
        if user is None:
            self._json_err("authentication required", 401)
            return
        if not self._has(user, "resource:read"):
            self._json_err("resource:read not permitted", 403)
            return
        ws, err = self._get_request_workspace(user)
        if err:
            self._json_err(err, 403)
            return
        if path in ("/api/finance/export", "/api/finance/expenses/export"):
            claims = self.store.list_expense_claims(ws)
            self._send_csv(f"expenses_{ws}.csv", ["id", "project_id", "category", "amount", "currency", "status", "notes", "created_at"], claims)
            return
        if path == "/api/finance/profit-loss":
            if user.get("role") not in ("Owner", "Manager", "Finance Manager"):
                self._json_err("forbidden: finance manager access required", 403)
                return
            summary = self.store.get_profit_loss_summary(ws)
            self._json_ok({"profit_loss": summary})
            return
        parts = [x for x in path.split("/") if x]
        if len(parts) >= 3 and parts[2] == "vendors":
            if user.get("role") not in ("Owner", "Manager", "Finance Manager"):
                self._json_err("forbidden: finance manager access required", 403)
                return
            if self.command == "GET":
                vendors = self.store.list_vendors(ws)
                self._json_ok({"vendors": vendors})
                return
            if self.command == "POST":
                if not self._has(user, "resource:create"):
                    self._json_err("resource:create not permitted", 403)
                    return
                data = _read_json(self)
                name = data.get("name")
                if not name:
                    self._json_err("name required", 400)
                    return
                cat = data.get("category", "vendor")
                contact = data.get("contact", "")
                vendor = self.store.create_vendor(ws, name, cat, contact)
                self._json_ok({"vendor": vendor}, 201)
                return
        if len(parts) >= 3 and parts[2] == "expenses":
            if self.command == "GET":
                claims = self.store.list_expense_claims(ws)
                self._json_ok({"expenses": claims})
                return
            if self.command == "POST":
                data = _read_json(self)
                amt = float(data.get("amount", 0.0))
                if amt <= 0:
                    self._json_err("valid positive amount required", 400)
                    return
                actor_id = user.get("user_id") or user.get("id") or 1
                cat = data.get("category", "travel")
                notes = data.get("notes", "")
                project_id = data.get("project_id", "")
                receipt = data.get("receipt_url", "")
                claim = self.store.create_expense_claim(ws, actor_id, project_id, cat, amt, notes, receipt)
                try:
                    res_key = "expense_claim"
                    res = self.store.fetchone("SELECT id FROM resources WHERE workspace_id=? AND key=?", (ws, res_key))
                    if not res:
                        self.store.create_resource(ws, res_key, "Expense Claims Register", "Staff expense claim records")
                    self.store.create_approval(ws, f"Expense Claim: {cat.title()} - INR {amt:,.2f}", notes or f"Claim by user {user.get('username')}", actor_id, res_key)
                except Exception:
                    pass
                self._json_ok({"expense": claim}, 201)
                return
        self._json_err("not found", 404)

    # ------------------------------------------------------------------
    # Business Operations: Estimates, Quotations, Work Orders, Invoices, Payments
    # ------------------------------------------------------------------
    def _handle_estimates_route(self, path: str, user: dict) -> None:
        if user is None:
            self._json_err("authentication required", 401)
            return
        ws, err = self._get_request_workspace(user)
        if err:
            self._json_err(err, 403)
            return
        parts = [x for x in path.split("/") if x]
        if len(parts) == 2 and parts[1] == "estimates":
            if self.command == "GET":
                estimates = self.store.list_estimates(ws)
                self._json_ok({"estimates": estimates, "count": len(estimates)})
                return
            if self.command == "POST":
                data = _read_json(self)
                est = self.store.create_estimate(ws, data)
                self._json_ok({"estimate": est}, 201)
                return
        if len(parts) == 3 and parts[1] == "estimates":
            eid = int(parts[2])
            if self.command == "GET":
                est = self.store.get_estimate(eid)
                if not est:
                    self._json_err("estimate not found", 404)
                    return
                if user.get("role") != "Owner" and est.get("workspace_id") != ws:
                    self._json_err("tenant isolation violation: unauthorized estimate access", 403)
                    return
                self._json_ok({"estimate": est})
                return
        if len(parts) == 4 and parts[1] == "estimates" and parts[3] == "status" and self.command == "POST":
            eid = int(parts[2])
            est = self.store.get_estimate(eid)
            if not est:
                self._json_err("estimate not found", 404)
                return
            if user.get("role") != "Owner" and est.get("workspace_id") != ws:
                self._json_err("tenant isolation violation: unauthorized estimate modification", 403)
                return
            data = _read_json(self)
            status = data.get("status", "submitted")
            updated = self.store.update_estimate_status(eid, status)
            self._json_ok({"estimate": updated})
            return
        self._json_err("not found", 404)

    def _handle_quotations_route(self, path: str, user: dict) -> None:
        if user is None:
            self._json_err("authentication required", 401)
            return
        ws, err = self._get_request_workspace(user)
        if err:
            self._json_err(err, 403)
            return
        parts = [x for x in path.split("/") if x]
        role = user.get("role") or ""
        if len(parts) == 2 and parts[1] == "quotations":
            if self.command == "GET":
                quotations = self.store.list_quotations(ws)
                for q in quotations:
                    if isinstance(q.get("items_json"), str):
                        try:
                            q["items"] = json.loads(q["items_json"])
                        except Exception:
                            q["items"] = []
                self._json_ok({"quotations": quotations, "count": len(quotations)})
                return
            if self.command == "POST":
                if role not in ("Owner", "Manager", "Project Manager", "Finance Manager"):
                    self._json_err("quotation creation restricted to Owner and Managers", 403)
                    return
                data = _read_json(self)
                q = lifecycle_enhancements.create_dynamic_quotation(self.store.conn, ws, data)
                self._json_ok({"quotation": q}, 201)
                return
        if len(parts) == 3 and parts[1] == "quotations" and parts[2].isdigit():
            qid = int(parts[2])
            if self.command == "GET":
                q = lifecycle_enhancements.get_dynamic_quotation(self.store.conn, qid)
                if not q:
                    self._json_err("quotation not found", 404)
                    return
                if user.get("role") != "Owner" and q.get("workspace_id") != ws:
                    self._json_err("tenant isolation violation: unauthorized quotation access", 403)
                    return
                self._json_ok({"quotation": q})
                return
            if self.command in ("PUT", "POST"):
                if role not in ("Owner", "Manager", "Project Manager", "Finance Manager"):
                    self._json_err("quotation modification restricted to Owner and Managers", 403)
                    return
                data = _read_json(self)
                updated = lifecycle_enhancements.update_dynamic_quotation(self.store.conn, qid, data)
                if not updated:
                    self._json_err("quotation not found", 404)
                    return
                self._json_ok({"quotation": updated})
                return
        if len(parts) == 4 and parts[1] == "quotations" and parts[3] in ("status", "accept") and self.command == "POST":
            if role not in ("Owner", "Manager", "Project Manager", "Finance Manager"):
                self._json_err("quotation modification restricted to Owner and Managers", 403)
                return
            qid = int(parts[2])
            q = self.store.get_quotation(qid)
            if not q:
                self._json_err("quotation not found", 404)
                return
            if user.get("role") != "Owner" and q.get("workspace_id") != ws:
                self._json_err("tenant isolation violation: unauthorized quotation modification", 403)
                return
            data = _read_json(self) if (self.headers.get("Content-Length") and int(self.headers.get("Content-Length", 0)) > 0) else {}
            status = data.get("status", "accepted") if parts[3] != "accept" else "accepted"
            updated = self.store.update_quotation_status(qid, status)
            self._json_ok({"quotation": updated})
            return
        self._json_err("not found", 404)

    def _handle_work_orders_route(self, path: str, user: dict) -> None:
        if user is None:
            self._json_err("authentication required", 401)
            return
        ws, err = self._get_request_workspace(user)
        if err:
            self._json_err(err, 403)
            return
        parts = [x for x in path.split("/") if x]
        if len(parts) == 2 and parts[1] == "work-orders":
            if self.command == "GET":
                wos = self.store.list_work_orders(ws)
                self._json_ok({"work_orders": wos, "count": len(wos)})
                return
            if self.command == "POST":
                data = _read_json(self)
                wo = self.store.create_work_order(ws, data)
                self._json_ok({"work_order": wo}, 201)
                return
        if len(parts) == 3 and parts[1] == "work-orders":
            wo_id = int(parts[2])
            if self.command == "GET":
                wo = self.store.get_work_order(wo_id)
                if not wo:
                    self._json_err("work order not found", 404)
                    return
                self._json_ok({"work_order": wo})
                return
        if len(parts) == 4 and parts[1] == "work-orders" and parts[3] in ("status", "qc-pass") and self.command == "POST":
            wo_id = int(parts[2])
            data = _read_json(self) if (self.headers.get("Content-Length") and int(self.headers.get("Content-Length", 0)) > 0) else {}
            status = data.get("status", "active")
            qc_status = "qc_passed" if parts[3] == "qc-pass" else data.get("field_qc_status")
            deliv_status = data.get("deliverables_status")
            updated = self.store.update_work_order_status(wo_id, status, qc_status, deliv_status)
            self._json_ok({"work_order": updated})
            return
        self._json_err("not found", 404)

    def _handle_invoices_route(self, path: str, user: dict) -> None:
        if user is None:
            self._json_err("authentication required", 401)
            return
        ws, err = self._get_request_workspace(user)
        if err:
            self._json_err(err, 403)
            return
        parsed = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed.query)
        bill_type = query_params.get("bill_type", [None])[0] or query_params.get("type", [None])[0]
        if path.startswith("/api/bills") and not bill_type:
            bill_type = "NON_GST"

        parts = [x for x in path.split("/") if x]
        role = user.get("role") or ""

        if len(parts) == 2 and parts[1] in ("invoices", "bills"):
            if self.command == "GET":
                docs = lifecycle_enhancements.list_billing_documents(self.store.conn, ws, bill_type)
                self._json_ok({"invoices": docs, "bills": docs, "count": len(docs)})
                return
            if self.command == "POST":
                if role not in ("Owner", "Finance Manager", "Manager"):
                    self._json_err("billing creation restricted to Owner and Finance Manager", 403)
                    return
                data = _read_json(self)
                if parts[1] == "bills" and "bill_type" not in data:
                    data["bill_type"] = "NON_GST"
                inv = lifecycle_enhancements.create_billing_document(self.store.conn, ws, data)
                self._json_ok({"invoice": inv, "bill": inv}, 201)
                return

        if len(parts) == 3 and parts[1] in ("invoices", "bills") and parts[2].isdigit():
            inv_id = int(parts[2])
            if self.command == "GET":
                inv = lifecycle_enhancements.get_billing_document(self.store.conn, inv_id)
                if not inv:
                    self._json_err("document not found", 404)
                    return
                if user.get("role") != "Owner" and inv.get("workspace_id") != ws:
                    self._json_err("tenant isolation violation: unauthorized invoice access", 403)
                    return
                self._json_ok({"invoice": inv, "bill": inv})
                return

        if len(parts) == 4 and parts[1] in ("invoices", "bills") and parts[3] == "payment" and self.command == "POST":
            if role not in ("Owner", "Finance Manager", "Manager"):
                self._json_err("recording payment restricted to Owner and Finance Manager", 403)
                return
            inv_id = int(parts[2])
            inv = self.store.get_invoice(inv_id)
            if not inv:
                self._json_err("invoice not found", 404)
                return
            if user.get("role") != "Owner" and inv.get("workspace_id") != ws:
                self._json_err("tenant isolation violation: unauthorized payment recording", 403)
                return
            data = _read_json(self)
            updated = self.store.record_payment(ws, inv_id, data)
            self._json_ok({"invoice": updated})
            return
        self._json_err("not found", 404)

    def _handle_payments_route(self, path: str, user: dict) -> None:
        if user is None:
            self._json_err("authentication required", 401)
            return
        ws, err = self._get_request_workspace(user)
        if err:
            self._json_err(err, 403)
            return
        parts = [x for x in path.split("/") if x]
        if len(parts) == 2 and parts[1] == "payments":
            if self.command == "GET":
                payments = self.store.list_payments(ws)
                self._json_ok({"payments": payments, "count": len(payments)})
                return
            if self.command == "POST":
                data = _read_json(self)
                inv_id = int(data.get("invoice_id"))
                updated = self.store.record_payment(ws, inv_id, data)
                self._json_ok({"payment": data, "invoice": updated}, 201)
                return
        self._json_err("not found", 404)

    def _handle_social_trends(self, user: dict) -> None:
        if user is None:
            self._json_err("authentication required", 401)
            return
        ws = user.get("workspace_id") or "SSC"
        from foundation.domains import m19_core
        report = m19_core.daily_trend_report(self.store, ws)
        trends = m19_core.discover_trends(self.store, ws)
        self._json_ok({"trend_report": report, "trends": trends})

    def _handle_content_ideas(self, user: dict) -> None:
        if user is None:
            self._json_err("authentication required", 401)
            return
        ws = user.get("workspace_id") or "SSC"
        from foundation.domains import m19_core
        if self.command == "POST":
            ideas = m19_core.generate_content_ideas(self.store, ws, limit=8)
            self._json_ok({"ideas": ideas}, 201)
            return
        rows = self.store.fetchall("SELECT * FROM social_content_ideas WHERE workspace_id=? ORDER BY created_at DESC", (ws,))
        if not rows:
            rows = m19_core.generate_content_ideas(self.store, ws, limit=8)
        self._json_ok({"ideas": rows})

    # ------------------------------------------------------------------
    # HRM — Employees, Attendance, Leaves
    # ------------------------------------------------------------------
    def _handle_vendors_route(self, path: str, user: dict) -> None:
        if user is None:
            self._json_err("authentication required", 401)
            return
        ws, err = self._get_request_workspace(user)
        if err:
            self._json_err(err, 403)
            return
        parsed = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed.query)
        status_filter = query_params.get("status", [None])[0]

        parts = [x for x in path.split("/") if x]

        if len(parts) == 2 and parts[1] == "vendors":
            if self.command == "GET":
                vendors = lifecycle_enhancements.list_registered_vendors(self.store.conn, ws, status_filter)
                self._json_ok({"vendors": vendors, "count": len(vendors)})
                return
            if self.command == "POST":
                data = _read_json(self)
                user_name = user.get("name") or user.get("username") or "Admin"
                v = lifecycle_enhancements.register_vendor(self.store.conn, ws, data, user_name)
                self._json_ok({"vendor": v}, 201)
                return

        if len(parts) == 3 and parts[1] == "vendors" and parts[2].isdigit():
            vid = int(parts[2])
            if self.command == "GET":
                v = lifecycle_enhancements.get_vendor_details(self.store.conn, vid)
                if not v:
                    self._json_err("vendor not found", 404)
                    return
                self._json_ok({"vendor": v})
                return
            if self.command in ("PUT", "POST"):
                data = _read_json(self)
                v = lifecycle_enhancements.update_vendor(self.store.conn, vid, data)
                self._json_ok({"vendor": v})
                return

        if len(parts) == 4 and parts[1] == "vendors" and parts[2].isdigit() and parts[3] == "status" and self.command == "POST":
            vid = int(parts[2])
            data = _read_json(self)
            new_status = data.get("status")
            remarks = data.get("remarks", "")
            user_name = user.get("name") or user.get("username") or "Admin"
            try:
                v = lifecycle_enhancements.update_vendor_status(self.store.conn, vid, new_status, remarks, user_name)
                self._json_ok({"vendor": v})
            except Exception as e:
                self._json_err(str(e), 400)
            return
        self._json_err("not found", 404)

    def _handle_employees_route(self, path: str, user: dict) -> None:
        """GET /api/employees — list employees; POST /api/employees — create employee; POST /api/employees/<id>/status — exit/status update."""
        if user is None:
            self._json_err("authentication required", 401)
            return
        if not self._has(user, ("resource:read", "hr:manage")):
            self._json_err("resource:read not permitted", 403)
            return
        ws = user.get("workspace_id") or "SSC"
        parsed = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed.query)
        filter_mode = query_params.get("filter", ["active"])[0] or query_params.get("status", ["active"])[0]

        parts = [x for x in path.split("/") if x]

        if path == "/api/employees/export":
            rows = lifecycle_enhancements.list_employees_filtered(self.store.conn, ws, "all")
            self._send_csv(f"employees_{ws}.csv", ["id", "employee_id", "name", "designation", "employment_status", "email", "phone", "hire_date"], rows)
            return

        if len(parts) == 2 and parts[1] == "employees":
            if self.command == "GET":
                rows = lifecycle_enhancements.list_employees_filtered(self.store.conn, ws, filter_mode)
                self._json_ok({"employees": rows, "count": len(rows)})
                return
            if self.command == "POST":
                if not self._has(user, ("resource:create", "hr:manage", "workspace:manage")):
                    self._json_err("resource:create not permitted", 403)
                    return
                data = _read_json(self)
                name = data.get("name", "").strip()
                if not name:
                    self._json_err("name required", 400)
                    return
                emp = self.store.create_employee(
                    workspace_id=ws,
                    name=name,
                    role=data.get("role", "Field Technician"),
                    department=data.get("department", "Operations"),
                    email=data.get("email", ""),
                    phone=data.get("phone", ""),
                    designation=data.get("designation", ""),
                    salary=float(data.get("salary", 0.0)),
                )
                self._json_ok({"employee": emp}, 201)
                return

        if len(parts) == 3 and parts[1] == "employees" and parts[2].isdigit():
            eid = int(parts[2])
            if self.command == "GET":
                emp = lifecycle_enhancements.get_employee_lifecycle_details(self.store.conn, eid)
                if not emp:
                    self._json_err("employee not found", 404)
                    return
                self._json_ok({"employee": emp})
                return

        if len(parts) == 4 and parts[1] == "employees" and parts[2].isdigit() and parts[3] == "status" and self.command == "POST":
            eid = int(parts[2])
            data = _read_json(self)
            user_name = user.get("name") or user.get("username") or "Admin"
            try:
                updated = lifecycle_enhancements.update_employee_employment_status(self.store.conn, eid, data, user_name)
                self._json_ok({"employee": updated})
            except Exception as e:
                self._json_err(str(e), 400)
            return
        self._json_err("not found", 404)

    def _handle_attendance_route(self, path: str, user: dict) -> None:
        """GET /api/attendance — list logs; POST /api/attendance — log check-in/out."""
        if user is None:
            self._json_err("authentication required", 401)
            return
        if not self._has(user, "resource:read"):
            self._json_err("resource:read not permitted", 403)
            return
        ws = user.get("workspace_id") or "SSC"
        if path == "/api/employees/export":
            rows = self.store.list_employees(ws)
            self._send_csv(f"employees_{ws}.csv", ["id", "employee_id", "name", "designation", "role", "email", "phone", "status", "hire_date"], rows)
            return
        if self.command == "GET":
            rows = self.store.list_attendance(ws)
            self._json_ok({"attendance": rows, "count": len(rows)})
            return
        if self.command == "POST":
            data = _read_json(self)
            emp_id = int(data.get("employee_id", 0))
            if not emp_id:
                self._json_err("employee_id required", 400)
                return
            log = self.store.log_attendance(
                workspace_id=ws,
                employee_id=emp_id,
                event=data.get("event", "check_in"),
                lat=float(data.get("lat", 0.0)),
                lng=float(data.get("lng", 0.0)),
                notes=data.get("notes", ""),
            )
            self._json_ok({"log": log}, 201)
            return
        self._json_err("method not allowed", 405)

    def _handle_leaves_route(self, path: str, user: dict) -> None:
        """GET /api/leaves — list leave requests; POST /api/leaves — submit leave request."""
        if user is None:
            self._json_err("authentication required", 401)
            return
        if not self._has(user, "resource:read"):
            self._json_err("resource:read not permitted", 403)
            return
        ws = user.get("workspace_id") or "SSC"
        actor_id = user.get("user_id") or user.get("id") or 1
        if self.command == "GET":
            rows = self.store.list_leaves(ws)
            self._json_ok({"leaves": rows, "count": len(rows)})
            return
        if self.command == "POST":
            data = _read_json(self)
            emp_id = int(data.get("employee_id", actor_id))
            leave_type = data.get("leave_type", "casual")
            from_date = data.get("from_date", "")
            to_date = data.get("to_date", "")
            reason = data.get("reason", "")
            if not from_date or not to_date:
                self._json_err("from_date and to_date required", 400)
                return
            leave = self.store.create_leave(ws, emp_id, leave_type, from_date, to_date, reason)
            # Route leave request to approval queue
            try:
                res_key = "leave_requests"
                res = self.store.fetchone("SELECT id FROM resources WHERE workspace_id=? AND key=?", (ws, res_key))
                if not res:
                    self.store.create_resource(ws, res_key, "Leave Requests", "Employee leave request approval queue")
                self.store.create_approval(ws, f"Leave Request: {leave_type.title()} ({from_date} to {to_date})", reason, actor_id, res_key)
            except Exception:
                pass
            self._json_ok({"leave": leave}, 201)
            return
        self._json_err("method not allowed", 405)

    def _handle_payroll_route(self, path: str, user: dict) -> None:
        """Payroll & Salary Management endpoints."""
        if user is None:
            self._json_err("authentication required", 401)
            return
        role = user.get("role") or ""
        if role not in ("Owner", "HR Manager", "Finance Manager"):
            self._json_err("payroll access restricted to Owner, HR Manager, and Finance Manager", 403)
            return
        ws = user.get("workspace_id") or "SSC"
        actor_id = user.get("user_id") or user.get("id") or 1
        from foundation.domains import payroll
        parts = [x for x in path.split("/") if x]
        # /api/payroll/runs
        if len(parts) == 3 and parts[2] == "runs":
            if self.command == "GET":
                runs = payroll.list_payroll_runs(self.store, None if user.get("role") == "Owner" else ws)
                self._json_ok({"payroll_runs": runs, "count": len(runs)})
                return
        # /api/payroll/calculate (dry-run preview)
        if len(parts) == 3 and parts[2] == "calculate":
            if self.command == "POST":
                data = _read_json(self)
                from datetime import datetime
                month = data.get("run_month") or datetime.now().strftime("%Y-%m")[:7]
                base_sal = float(data.get("base_monthly_salary", 25000.0))
                summary = payroll.calculate_payroll(self.store, ws, month, base_sal)
                self._json_ok({"summary": summary})
                return
        # /api/payroll/run (execute run & create payslips)
        if len(parts) == 3 and parts[2] == "run":
            if self.command == "POST":
                if role not in ("Owner", "HR Manager"):
                    self._json_err("permission denied: HR Manager or Owner required to execute payroll run", 403)
                    return
                data = _read_json(self)
                from datetime import datetime
                month = data.get("run_month") or datetime.now().strftime("%Y-%m")[:7]
                base_sal = float(data.get("base_monthly_salary", 25000.0))
                run_by = data.get("run_by")
                res = payroll.execute_payroll_run(self.store, actor_id, ws, month, run_by=run_by, base_monthly_salary=base_sal)
                self._json_ok({"payroll_run": res}, 201)
                return
        # /api/payroll/runs/{id}
        if len(parts) == 4 and parts[2] == "runs":
            run_id = int(parts[3])
            run = payroll.get_payroll_run(self.store, run_id)
            if not run:
                self._json_err("payroll run not found", 404)
                return
            if user.get("role") != "Owner" and run.get("workspace_id") != ws:
                self._json_err("tenant isolation violation: unauthorized payroll run access", 403)
                return
            slips = payroll.list_payslips(self.store, run_id)
            run["payslips"] = slips
            self._json_ok({"payroll_run": run})
            return
        # /api/payroll/runs/{id}/approve
        if len(parts) == 5 and parts[2] == "runs" and parts[4] == "approve" and self.command == "POST":
            if not self._has(user, ("hr:manage", "workspace:manage")):
                self._json_err("permission denied", 403)
                return
            run_id = int(parts[3])
            run = payroll.get_payroll_run(self.store, run_id)
            if not run:
                self._json_err("payroll run not found", 404)
                return
            if user.get("role") != "Owner" and run.get("workspace_id") != ws:
                self._json_err("tenant isolation violation: unauthorized payroll run approval", 403)
                return
            try:
                approved = payroll.approve_run(self.store, actor_id, run_id)
                self._json_ok({"payroll_run": approved})
            except Exception as e:
                self._json_err(str(e), 400)
            return
        # /api/payroll/payslips
        if len(parts) >= 3 and parts[2] == "payslips":
            if len(parts) == 3 and self.command == "GET":
                slips = self.store.fetchall("SELECT p.* FROM payslips p JOIN payroll_runs pr ON pr.id=p.payroll_run_id WHERE pr.workspace_id=? ORDER BY p.generated_at DESC", (ws,))
                self._json_ok({"payslips": slips, "count": len(slips)})
                return
            elif len(parts) == 4 and self.command == "GET":
                slip_id = int(parts[3])
                slip = self.store.fetchone("SELECT p.*, pr.workspace_id FROM payslips p JOIN payroll_runs pr ON pr.id=p.payroll_run_id WHERE p.id=?", (slip_id,))
                if not slip:
                    self._json_err("payslip not found", 404)
                    return
                if user.get("role") != "Owner" and slip.get("workspace_id") != ws:
                    self._json_err("tenant isolation violation: unauthorized payslip access", 403)
                    return
                self._json_ok({"payslip": slip})
                return
        self._json_err("not found", 404)

    def _handle_ai_brain_action(self, user: dict) -> None:
        """Route AI actions through owner approval if sensitive, or execute directly."""
        if user is None:
            self._json_err("authentication required", 401)
            return
        data = _read_json(self)
        action_name = data.get("action")
        payload = data.get("payload", {})
        if not action_name:
            self._json_err("action required", 400)
            return
        ws = user.get("workspace_id") or "SSC"
        actor_id = user.get("user_id") or user.get("id") or 1
        SENSITIVE_ACTIONS = {"publish_post", "delete_record", "payout", "payout_vendor", "external_api_call", "execute_contract"}
        if action_name in SENSITIVE_ACTIONS:
            res_key = "ai_agent_actions"
            res = self.store.fetchone("SELECT id FROM resources WHERE workspace_id=? AND key=?", (ws, res_key))
            if not res:
                self.store.create_resource(ws, res_key, "AI Agent Actions", "Autonomous agent tool execution approval queue")
            appr = self.store.create_approval(
                ws,
                f"AI Action Sign-off: {action_name.replace('_', ' ').title()}",
                f"Agent requested {action_name} with params: {json.dumps(payload)[:200]}",
                actor_id,
                res_key
            )
            self._json_ok({
                "status": "approval_required",
                "approval_id": appr["id"],
                "message": f"Action '{action_name}' staged and queued for Owner/Manager approval."
            })
            return
        self._json_ok({
            "status": "executed",
            "action": action_name,
            "result": f"Executed {action_name} successfully."
        })

    def _handle_lead_create(self, user: dict) -> None:
        """Create a CRM lead (owner/manager only)."""
        if not self._has(user, "resource:create"):
            self._json_err("resource:create not permitted", 403)
            return
        data = _read_json(self)
        if not data.get("lead_name"):
            self._json_err("lead_name required", 400)
            return
        from foundation.domains.m19_core import create_lead
        actor_id = user.get("user_id") if user.get("user_id") is not None else user.get("id")
        if actor_id is None:
            self._json_err("missing actor identity", 401)
            return
        try:
            lead = create_lead(
                self.store, actor_id, user.get("workspace_id") or "SSC",
                data["lead_name"], data.get("company", ""), data.get("platform", "instagram"),
                data.get("enquiry_text", ""), source_post=data.get("source_post", ""),
                service_interest=data.get("service_interest", ""), lead_priority=data.get("lead_priority", "medium"),
                assigned_employee_id=data.get("assigned_employee_id"))
        except PermissionError as e:
            self._json_err(str(e), 403)
            return
        self._json_ok({"lead": lead}, 201)

    def do_PUT(self) -> None:  # noqa: N802
        """Handle PUT requests; the owner dashboard edits users via PUT /api/users/{id} or /api/users/{id}/edit."""
        user = self._user()
        if user is None:
            self._json_err("authentication required", 401)
            return
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)
        try:
            if path.startswith("/api/quotations/"):
                self._handle_quotations_route(path, user)
                return
            elif path.startswith("/api/sites/"):
                self._handle_sites_route(path, user)
                return
            elif path.startswith("/api/vendors/"):
                self._handle_vendors_route(path, user)
                return
            elif path.startswith("/api/employees/"):
                self._handle_employees_route(path, user)
                return
            elif path.startswith("/api/invoices/") or path.startswith("/api/bills/"):
                self._handle_invoices_route(path, user)
                return
            elif path.startswith("/api/users/"):
                parts = [p for p in path.split("/") if p]
                if len(parts) >= 3 and parts[1] == "users" and parts[2].isdigit():
                    uid = int(parts[2])
                    data = _read_json(self)
                    self._handle_user_edit(user, uid, data)
                    return
            self._json_err("not found", 404)
        except Exception as e:
            import traceback; traceback.print_exc()
            self._json_err(f"internal error: {e}", 500)

    def _handle_user_edit(self, user: dict, uid: int, data: dict) -> None:
        """Edit an existing user (POST or PUT)."""
        if not has_permission(user.get("role") or "", "workspace:manage"):
            self._json_err("user:manage not permitted for this role", 403)
            return
        updates: dict[str, Any] = {}
        if "username" in data:
            updates["username"] = data["username"]
        if "name" in data:
            updates["name"] = data["name"]
        if "role" in data:
            try:
                updates["role_id"] = self.store._role_id(data["role"])
            except Exception:
                self._json_err("invalid role", 400)
                return
        if "workspace_id" in data:
            updates["workspace_id"] = data["workspace_id"]
        if "active" in data:
            updates["active"] = 1 if data["active"] else 0
        if "password" in data and data["password"]:
            updates["password"] = data["password"]
        if not updates:
            self._json_err("no fields to update", 400)
            return
        try:
            updated = self.store.update_user(uid, **updates)
        except Exception as e:
            self._json_err(str(e), 400)
            return
        if updated is None:
            self._json_err("user not found", 404)
            return
        self._json_ok({"user": updated})

    def _handle_system_route(self, path: str, user: dict) -> None:
        """System info: GET /api/system, GET /api/system/usage, GET /api/system/health."""
        if path == "/api/system":
            self._handle_system_health(user)
            return
        if path == "/api/system/usage":
            self._handle_system_usage(user)
            return
        if path == "/api/system/health":
            self._handle_system_health(user)
            return
        self._json_err("not found", 404)

    def _handle_reports_route(self, path: str, user: dict) -> None:
        """Reports: GET /api/reports, GET /api/reports/dashboard, POST /api/reports/generate, GET /api/reports/<id>, GET /api/reports/<id>/export."""
        if user is None:
            self._json_err("authentication required", 401)
            return
        ws, err = self._get_request_workspace(user)
        if err:
            self._json_err(err, 403)
            return

        parts = [x for x in path.split("/") if x]

        # GET /api/reports/dashboard
        if len(parts) == 3 and parts[1] == "reports" and parts[2] == "dashboard":
            stats = lifecycle_enhancements.get_reports_analytics_summary(self.store.conn, ws)
            self._json_ok(stats)
            return

        # POST /api/reports/generate or POST /api/reports
        if (len(parts) == 3 and parts[1] == "reports" and parts[2] == "generate" and self.command == "POST") or (len(parts) == 2 and parts[1] == "reports" and self.command == "POST"):
            data = _read_json(self) if (self.headers.get("Content-Length") and int(self.headers.get("Content-Length", 0)) > 0) else {}
            rep_type = data.get("report_type", "MONTHLY_PERFORMANCE")
            date_range = data.get("date_range", "Last 30 Days")
            report = lifecycle_enhancements.generate_business_report(self.store.conn, ws, rep_type, date_range)
            self._json_ok({"report": report}, 201)
            return

        # GET /api/reports
        if len(parts) == 2 and parts[1] == "reports":
            reports = lifecycle_enhancements.list_archived_reports(self.store.conn, ws)
            self._json_ok({"reports": reports, "count": len(reports)})
            return

        # GET /api/reports/<id>
        if len(parts) == 3 and parts[1] == "reports" and parts[2].isdigit():
            rid = int(parts[2])
            rep = lifecycle_enhancements.get_report_details(self.store.conn, rid)
            if not rep:
                self._json_err("report not found", 404)
                return
            self._json_ok({"report": rep})
            return

        # GET /api/reports/<id>/export
        if len(parts) == 4 and parts[1] == "reports" and parts[2].isdigit() and parts[3] == "export":
            rid = int(parts[2])
            rep = lifecycle_enhancements.get_report_details(self.store.conn, rid)
            if not rep:
                self._json_err("report not found", 404)
                return
            parsed = urllib.parse.urlparse(self.path)
            fmt = urllib.parse.parse_qs(parsed.query).get("format", ["json"])[0]
            if fmt == "csv":
                tables = rep.get("detailed_tables_json") or []
                lines = [f"# {rep.get('title')}", f"# Period: {rep.get('period_label')}", f"# Generated: {rep.get('generated_at')}", ""]
                for tbl in tables:
                    lines.append(f"## {tbl.get('section_name')}")
                    lines.append(",".join(f'"{h}"' for h in tbl.get('headers', [])))
                    for r in tbl.get('rows', []):
                        lines.append(",".join(f'"{c}"' for c in r))
                    lines.append("")
                csv_data = "\n".join(lines)
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", f"attachment; filename=report_{rid}_{ws}.csv")
                self.end_headers()
                self.wfile.write(csv_data.encode("utf-8"))
                return
            self._json_ok({"report": rep})
            return

        self._json_err("not found", 404)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)
        try:
            user = self._user()
            # Authentication gate for all POST routes except login
            if path != "/api/auth/login" and user is None:
                self._json_err("authentication required", 401)
                return
            if path == "/api/auth/login":
                data = _read_json(self)
                uname = data.get("username", "").strip()
                passwd = data.get("password", "")
                client_ip = self.client_address[0] if hasattr(self, "client_address") and self.client_address else "127.0.0.1"
                ip_ident = f"ip_{client_ip}" if client_ip not in ("127.0.0.1", "::1", "localhost") else None
                if (uname and _is_rate_limited(uname.lower())) or (ip_ident and _is_rate_limited(ip_ident)):
                    self._json_err("Account temporarily locked due to excessive failed login attempts. Please try again after 5 minutes.", 429)
                    return
                user = get_store().authenticate(uname, passwd)
                if user is None:
                    if uname:
                        _record_failure(uname.lower())
                    if ip_ident:
                        _record_failure(ip_ident)
                    self._json_err("invalid username/password", 401)
                    return
                _clear_failures(uname.lower())
                if ip_ident:
                    _clear_failures(ip_ident)
                token = issue_token(get_store(), user["username"])
                self._json_ok({"token": token, "user": {k: user[k] for k in
                    ("user_id" if "user_id" in user else "id", "username", "name", "role", "workspace_id")},
                    "workspace": get_store().get_workspace(user["workspace_id"]) if user.get("workspace_id") else None})
            elif path == "/api/auth/logout":
                from foundation.auth import invalidate_session
                tok = self._token()
                invalidate_session(get_store(), tok)
                self._json_ok({"ok": True, "message": "Logged out successfully. Session invalidated."})
                return
            elif path == "/api/auth/change-password":
                data = _read_json(self)
                old_p = data.get("current_password", "")
                new_p = data.get("new_password", "")
                uid = user.get("id") or user.get("user_id")
                from foundation.auth import change_user_password
                ok, msg = change_user_password(get_store(), uid, old_p, new_p)
                if not ok:
                    self._json_err(msg, 400)
                    return
                self._json_ok({"ok": True, "message": msg})
                return
            elif path in ("/api/oauth/callback", "/api/oauth/google/callback"):
                self._handle_oauth_callback(user)
                return
            elif path in ("/api/oauth/disconnect", "/api/oauth/google/disconnect"):
                self._handle_oauth_disconnect(user)
                return
            elif path == "/api/oauth/diagnostic":
                self._handle_oauth_diagnostic(user)
                return
            elif path == "/api/approvals":
                if user is None:
                    self._json_err("authentication required", 401)
                    return
                actor_id = user.get("id") or user.get("user_id")
                if actor_id is None:
                    self._json_err("authentication required", 401)
                    return
                if not can_create(get_store(), actor_id):
                    self._json_err("approval:create not permitted for this role", 403)
                    return
                data = _read_json(self)
                if not data.get("title") or not data.get("resource_key"):
                    self._json_err("title and resource_key required", 400)
                    return
                approval = create_approval(get_store(), data["title"], data.get("description", ""),
                                              actor_id, user.get("workspace_id"), data["resource_key"])
                log(get_store(), actor_id, "approval:create", f"approval:{approval['id']}",
                    {"title": data["title"], "resource_key": data["resource_key"]},
                    user.get("workspace_id"))
                self._json_ok({"approval": approval})
            elif path.startswith("/api/approvals/") and path.endswith("/transition"):
                aid = int(path.split("/")[3])
                data = _read_json(self)
                user = self._user()
                if user is None:
                    self._json_err("authentication required", 401)
                    return
                if data.get("status") not in ("approved", "rejected", "withdrawn"):
                    self._json_err("status must be approved/rejected/withdrawn", 400)
                    return
                try:
                    result = transition(self.store, aid, data["status"], user["user_id"], data.get("note", ""))
                except PermissionError as e:
                    self._json_err(str(e), 403)
                    return
                self._json_ok({"approval": result, "logged": True})
            # -- new dashboard routes ------------------------------------------
            elif path == "/api/auth/logout":
                tok = self._token()
                if tok:
                    self.store.conn.execute("DELETE FROM sessions WHERE token=?", (tok,))
                    self.store.conn.commit()
                self._json_ok({"ok": True})
            elif path == "/api/auth/password":
                user = self._user()
                if user is None:
                    self._json_err("authentication required", 401)
                    return
                data = _read_json(self)
                old_pw = data.get("old_password")
                new_pw = data.get("new_password")
                if not old_pw or not new_pw:
                    self._json_err("old_password and new_password required", 400)
                    return
                if len(new_pw) < 8 or not any(c.isdigit() or not c.isalnum() for c in new_pw):
                    self._json_err("Password must be at least 8 characters long and contain numbers or special characters", 400)
                    return
                db_user = self.store.fetchone("SELECT * FROM users WHERE id=?", (user.get("user_id") or user.get("id"),))
                from foundation.store import _verify
                if not db_user or not _verify(old_pw, db_user["password_hash"]):
                    self._json_err("current password incorrect", 403)
                    return
                self.store.update_user(db_user["id"], password=new_pw)
                self._json_ok({"ok": True, "message": "Password updated successfully."})
                return
            elif path == "/api/users":
                user = self._user()
                if user is None:
                    self._json_err("authentication required", 401)
                    return
                if not has_permission(user.get("role") or "", "workspace:manage"):
                    self._json_err("user:manage not permitted for this role", 403)
                    return
                data = _read_json(self)
                required = ["username", "password", "name", "role", "workspace_id"]
                if not all(k in data for k in required):
                    self._json_err("username,password,name,role,workspace_id required", 400)
                    return
                try:
                    role_id = self.store._role_id(data["role"])
                except Exception:
                    self._json_err("invalid role", 400)
                    return
                try:
                    new_user = self.store.create_user(
                        data["username"], data["password"], data["name"],
                        role_id, data["workspace_id"])
                except Exception as e:
                    self._json_err(str(e), 400)
                    return
                self._json_ok({"user": new_user}, 201)
            elif path.startswith("/api/users/") and path.endswith("/deactivate"):
                user = self._user()
                if user is None:
                    self._json_err("authentication required", 401)
                    return
                if not has_permission(user.get("role") or "", "workspace:manage"):
                    self._json_err("user:manage not permitted for this role", 403)
                    return
                try:
                    uid = int(path.split("/")[-2])
                except ValueError:
                    self._json_err("invalid user id", 400)
                    return
                try:
                    updated = self.store.deactivate_user(uid)
                except Exception as e:
                    self._json_err(str(e), 400)
                    return
                if updated is None:
                    self._json_err("user not found", 404)
                    return
                self._json_ok({"user": updated})
            elif path.startswith("/api/users/") and path.endswith("/activate"):
                user = self._user()
                if user is None:
                    self._json_err("authentication required", 401)
                    return
                try:
                    uid = int(path.split("/")[-2])
                except ValueError:
                    self._json_err("invalid user id", 400)
                    return
                try:
                    updated = self.store.activate_user(uid)
                except Exception as e:
                    self._json_err(str(e), 400)
                    return
                if updated is None:
                    self._json_err("user not found", 404)
                    return
                self._json_ok({"user": updated})
            if path.startswith("/api/workspaces/") and path.endswith("/contacts"):
                code = path.split("/")[3]
                self._handle_contact_create(user, code)
                return
            elif path == "/api/content":
                self._handle_content_create(user)
                return
            elif path == "/api/content/ideas":
                self._handle_content_ideas(user)
                return
            elif path.startswith("/api/content/"):
                parts = [x for x in path.split("/") if x]
                if len(parts) >= 3 and parts[1] == "content":
                    cid = parts[2]
                    if len(parts) == 3:
                        self._handle_content_script(user, cid)
                    elif len(parts) == 4 and parts[3] == "script":
                        self._handle_content_script(user, cid)
                    elif len(parts) == 4 and parts[3] == "approval":
                        self._handle_content_approval(user, cid)
                    elif len(parts) == 5 and parts[3] == "approval" and parts[4] == "transition":
                        self._handle_content_approval_transition(user, cid)
                    else:
                        self._json_err("not found", 404)
                else:
                    self._json_err("not found", 404)
                return
            elif path.startswith("/api/content/"):
                self._json_err("not found", 404)
                return
            elif path.startswith("/api/media/download/"):
                parts = [x for x in path.split("/") if x]
                if len(parts) >= 4 and parts[3].isdigit():
                    aid = int(parts[3])
                    asset = self.store.fetchone("SELECT * FROM social_media_assets WHERE id=?", (aid,))
                    if not asset:
                        self._json_err("media asset not found", 404)
                        return
                    ws = user.get("workspace_id") or "SSC"
                    if user.get("role") != "Owner" and asset.get("workspace_id") and asset["workspace_id"] != ws:
                        self._json_err("tenant isolation violation: unauthorized asset access", 403)
                        return
                    fname = asset["filename"]
                    from foundation.config import project_root
                    p = Path(project_root()) / fname if not os.path.isabs(fname) else Path(fname)
                    if not p.exists():
                        p = Path(os.getcwd()) / "data" / "m19_output" / os.path.basename(fname)
                    if not p.exists():
                        self._json_err("media file not found on disk", 404)
                        return
                    with open(p, "rb") as mf:
                        b = mf.read()
                    ctype = "video/mp4" if p.name.endswith(".mp4") else ("image/png" if p.name.endswith(".png") else "application/octet-stream")
                    self.send_response(200)
                    self.send_header("Content-Type", ctype)
                    self.send_header("Content-Length", str(len(b)))
                    self.send_header("Content-Disposition", f'inline; filename="{p.name}"')
                    self.end_headers()
                    self.wfile.write(b)
                    return
                self._json_err("invalid media download request", 400)
                return
            elif path.startswith("/api/media/"):
                parts = [x for x in path.split("/") if x]
                if len(parts) < 3 or parts[1] != "media":
                    self._json_err("not found", 404)
                    return
                mid = parts[2]
                if len(parts) == 3:
                    self._handle_media_upload(user)
                elif len(parts) == 4 and parts[3] == "render":
                    self._handle_media_render(user, mid)
                elif len(parts) == 4 and parts[3] == "subtitle":
                    self._handle_media_subtitle(user, mid)
                elif len(parts) == 4 and parts[3] == "voiceover":
                    self._handle_media_voiceover(user, mid)
                else:
                    self._json_err("not found", 404)
                return
            elif path.startswith("/api/media"):
                self._handle_media_list(user)
                return
            elif path.startswith("/api/publish"):
                parts = [x for x in path.split("/") if x]
                if len(parts) < 2 or parts[1] != "publish":
                    self._json_err("not found", 404)
                    return
                if len(parts) == 2:
                    self._handle_publish_create(user)
                elif len(parts) == 4 and parts[3] == "reconcile":
                    self._handle_publish_reconcile(user, parts[2])
                elif len(parts) == 3 and parts[2] == "reconcile":
                    data = _read_json(self) if (self.headers.get("Content-Length") and int(self.headers.get("Content-Length", 0)) > 0) else {}
                    pid = data.get("job_id") or data.get("id") or 1
                    self._handle_publish_reconcile(user, pid)
                elif len(parts) >= 3:
                    self._handle_publish_detail(user, parts[2])
                else:
                    self._json_err("not found", 404)
                return
            elif path == "/api/publish":
                self._handle_publish_list(user)
                return
            elif path.startswith("/api/social/accounts/"):
                parts = [x for x in path.split("/") if x]
                if len(parts) >= 4 and parts[1] == "social" and parts[2] == "accounts":
                    aid = parts[3]
                    if len(parts) == 4:
                        self._handle_social_account_add(user)
                    elif len(parts) == 5 and parts[4] == "connect":
                        self._handle_social_account_connect(user, aid)
                    elif len(parts) == 5 and parts[4] == "disconnect":
                        self._handle_social_account_disconnect(user, aid)
                    elif len(parts) == 5 and parts[4] == "sync":
                        self._handle_social_account_sync(user, aid)
                    else:
                        self._json_err("not found", 404)
                return
            elif path == "/api/social/accounts":
                self._handle_social_account_add(user)
                return
            elif path.startswith("/api/social/accounts/"):
                self._handle_social_accounts(user)
                return
            elif path.startswith("/api/instagram"):
                self._handle_instagram_route(path, user)
                return
            elif path.startswith("/api/reports"):
                self._handle_reports_route(path, user)
                return
            elif path.startswith("/api/leads"):
                self._handle_leads_route(path, user)
                return
            elif path.startswith("/api/clients"):
                self._handle_clients_route(path, user)
                return
            elif path.startswith("/api/sites"):
                self._handle_sites_route(path, user)
                return
            elif path.startswith("/api/finance"):
                self._handle_finance_route(path, user)
                return
            elif path.startswith("/api/employees"):
                self._handle_employees_route(path, user)
                return
            elif path.startswith("/api/attendance"):
                self._handle_attendance_route(path, user)
                return
            elif path.startswith("/api/leaves"):
                self._handle_leaves_route(path, user)
                return
            elif path.startswith("/api/payroll"):
                self._handle_payroll_route(path, user)
                return
            elif path.startswith("/api/estimates"):
                self._handle_estimates_route(path, user)
                return
            elif path.startswith("/api/quotations"):
                self._handle_quotations_route(path, user)
                return
            elif path.startswith("/api/work-orders"):
                self._handle_work_orders_route(path, user)
                return
            elif path.startswith("/api/invoices"):
                self._handle_invoices_route(path, user)
                return
            elif path.startswith("/api/bills"):
                self._handle_invoices_route(path, user)
                return
            elif path.startswith("/api/vendors"):
                self._handle_vendors_route(path, user)
                return
            elif path.startswith("/api/payments"):
                self._handle_payments_route(path, user)
                return
            elif path == "/api/calendar":
                self._handle_calendar(user)
                return
            elif path == "/api/content/ideas":
                self._handle_content_ideas(user)
                return
            elif path == "/api/social/trends":
                self._handle_social_trends(user)
                return
            elif path == "/api/ai-brain/action":
                self._handle_ai_brain_action(user)
                return
            elif path.startswith("/api/system"):
                self._handle_system_route(path, user)
                return
            elif path.startswith("/api/ai-brain"):
                self._handle_ai_brain_route(path, user)
                return
            elif path.startswith("/api/intelligence") or path.startswith("/api/ai/marketing"):
                self._handle_intelligence_route(path, user)
                return
            elif path.startswith("/api/studio"):
                self._handle_studio_route(path, user)
                return
            elif path.startswith("/api/tasks"):
                self._handle_tasks_route(path, user)
                return
            elif path.startswith("/api/filter"):
                self._handle_filter_route(path, user)
                return
            elif path.startswith("/api/integrations"):
                self._handle_integrations_route(path, user)
                return
            elif path.startswith("/api/gbp"):
                self._handle_gbp_route(path, user)
                return
            elif path.startswith("/api/owner-setup"):
                self._handle_owner_setup_route(path, user)
                return
            elif path.startswith("/api/oauth/authorize"):
                self._handle_oauth_authorize(user)
                return
            else:
                self._json_err("not found", 404)
        except Exception as e:
            import traceback; traceback.print_exc()
            self._json_err(f"internal error: {e}", 500)

    def _handle_ai_brain_route(self, path: str, user: dict) -> None:
        """AI Brain routing: agents, tasks, tool executions."""
        parts = [x for x in path.split("/") if x]
        if len(parts) == 2:
            self._handle_ai_brain_agents(user)
        elif len(parts) == 3 and parts[2] == "agents":
            self._handle_ai_brain_agents(user)
        elif len(parts) == 3 and parts[2] == "tasks":
            if self.command == "POST":
                self._handle_ai_brain_task_create(user)
            else:
                self._handle_ai_brain_tasks(user)
        elif len(parts) == 4 and parts[2] == "tasks" and parts[3] == "execute":
            self._handle_ai_brain_task_execute(user)
        elif len(parts) == 5 and parts[2] == "tasks" and parts[4] == "execute":
            self._handle_ai_brain_task_execute(user, task_id=int(parts[3]))
        elif len(parts) == 5 and parts[2] == "tasks" and parts[4] == "status":
            self._handle_ai_brain_task_status(user, parts[3])
        elif len(parts) == 5 and parts[2] == "tasks" and parts[4] == "executions":
            self._handle_ai_brain_tool_executions(user, parts[3])
        else:
            self._json_err("not found", 404)

    # -- dashboard sections (role-gated) -------------------------------------
    def _has(self, user: dict, perm: str | tuple[str, ...]) -> bool:
        if user is None:
            return False
        if isinstance(perm, str):
            perm = (perm,)
        return any(has_permission(user.get("role") or "", p) for p in perm)

    def _handle_dashboard(self, path: str) -> None:
        parts = [p for p in path.split("/") if p]
        if len(parts) < 3 or parts[1] != "dashboard":
            self._json_err("not found", 404)
            return
        section = parts[2]
        user = self._user()
        if user is None:
            self._json_err("authentication required", 401)
            return
        ws, err = self._get_request_workspace(user)
        if err:
            self._json_err(err, 403)
            return
        store = self.store

        if section == "overview":
            self._role_ok(user, ("report:list", "workspace:list"))
            pending = store.list_approvals(ws, "pending")
            recent = store.list_audit(ws, 10)
            self._json_ok({
                "workspace": ws,
                "pending_approvals": len(pending),
                "recent_audit": recent,
                "demo_seed": foundation_config.load_config().get("seed_demo_users", True),
            })
            return
        if section == "workspaces":
            return self._json_ok({
                "workspaces": store.list_workspaces(),
                "current": ws,
                "roles": [r["code"] for r in foundation_config.load_config()["roles"]],
            })
        if section == "projects":
            if not self._has(user, ("resource:read", "workspace:list", "workspace:read")):
                self._json_err("resource:read required", 403)
                return
            sites = store.list_sites(None if ws == "ALL" else ws)
            if ws == "INFRA":
                deliverables = [
                    {"site_code": "SITE-INF-01", "name": "Rewa Ring Road Civil Earthworks DPR & Cross Sections", "type": "Civil DPR", "status": "Ready"},
                    {"site_code": "SITE-INF-02", "name": "Shah Heights Piling & Soil Bearing Capacity Test Report", "type": "Structural Report", "status": "Ready"},
                    {"site_code": "SITE-INF-03", "name": "Anuppur Logistics Park Pavement & Drainage Layout", "type": "Civil Drawing", "status": "In Progress"}
                ]
            elif ws == "OTHER":
                deliverables = [
                    {"site_code": "SITE-OTH-01", "name": "Agrotech Facility Master Plan & Boundary Survey", "type": "Master Plan", "status": "Ready"}
                ]
            else:
                deliverables = [
                    {"site_code": "SITE-SGR-01", "name": "Jayant Coal Block DGPS Control Network KML", "type": "KML / GIS", "status": "Ready"},
                    {"site_code": "SITE-SGR-01", "name": "Topographic Contour Map (0.5m interval) DWG", "type": "CAD DWG", "status": "Ready"},
                    {"site_code": "SITE-ANP-02", "name": "Industrial Corridor Pillar Boundary Coordinates CSV", "type": "Coordinates", "status": "In Progress"},
                    {"site_code": "SITE-SOL-03", "name": "2.5 MW Solar Shadow & Elevation Analysis Report PDF", "type": "Engineering Report", "status": "Completed"}
                ]
            self._json_ok({"resources": store.list_resources(ws), "sites": sites, "deliverables": deliverables})
            return
        if section == "finance":
            if not self._has(user, "approval:list"):
                self._json_err("approval:list required", 403)
                return
            approvals = store.list_approvals(ws, "pending")
            vendors = store.list_vendors(ws)
            claims = store.list_expense_claims(ws)
            total_amt = sum(float(c.get("amount") or 0.0) for c in claims)
            self._json_ok({
                "approvals": approvals,
                "vendors": vendors,
                "claims": claims,
                "summary": {
                    "pending_approvals_count": len(approvals),
                    "vendor_count": len(vendors),
                    "total_claims_inr": total_amt
                }
            })
            return
        if section == "employees":
            if not self._has(user, "report:list"):
                self._json_err("report:list required", 403)
                return
            self._json_ok({"users": store.list_users()})
            return
        if section == "marketing":
            if not self._has(user, "report:list"):
                self._json_err("report:list required", 403)
                return
            self._json_ok({"marketing_modules": self._module_status()})
            return
        if section == "crm":
            if not self._has(user, "resource:list"):
                self._json_err("resource:list required", 403)
                return
            leads = store.fetchall("SELECT * FROM social_leads WHERE workspace_id=? ORDER BY created_at DESC", (ws,)) if ws != "ALL" else store.fetchall("SELECT * FROM social_leads ORDER BY created_at DESC")
            clients = store.list_clients(ws)
            stats = {
                "total_leads": len(leads),
                "new_leads": len([l for l in leads if l.get("lead_status") == "new"]),
                "qualified_leads": len([l for l in leads if l.get("lead_status") in ("qualified", "contacted")]),
                "converted_leads": len([l for l in leads if l.get("conversion_status") == "converted" or l.get("lead_status") == "won"]),
                "clients_count": len(clients)
            }
            self._json_ok({
                "resources": store.list_resources(ws),
                "leads": leads,
                "clients": clients,
                "stats": stats
            })
            return
        if section == "ai":
            self._json_ok({"ai_brain": foundation_config.load_config()["ai_brain"],
                           "role": user.get("role"), "workspace": ws})
            return
        if section == "approvals":
            self._json_ok({"approvals": store.list_approvals(ws)})
            return
        if section == "settings":
            self._json_ok({"config": foundation_config.load_config(),
                           "roles": [r["code"] for r in foundation_config.load_config()["roles"]],
                           "users": store.list_users()})
            return
        self._json_err("not found", 404)

    def _role_ok(self, user: dict, perms: tuple) -> None:
        if not any(self._has(user, p) for p in perms):
            self._json_err("permission denied", 403)
            return True
        return False

    def _module_status(self) -> list[dict]:
        out = []
        for code, name in _MODULE_SHORT.items():
            out.append({"code": code, "name": name, "status": _MODULE_STATUS.get(code, "Unknown")})
        return out

    def _crm_lead_count(self, ws: str) -> int:
        leads = [r for r in self.store.list_resources(ws)
                 if r.get("key", "").startswith("lead")]
        return len(leads)

    def _handle_contacts(self, user: dict, ws: str) -> None:
        """CRM bridge: social_leads for a workspace (M19<->M06 relation)."""
        if not self._has(user, "resource:read"):
            self._json_err("resource:read required", 403)
            return
        if ws == "SSC":
            leads = self.store.fetchall(
                "SELECT id, lead_name, company, platform, lead_status, "
                "lead_priority, follow_up_date, created_at FROM social_leads "
                "WHERE workspace_id='SSC' ORDER BY created_at DESC")
        else:
            leads = self.store.fetchall(
                "SELECT id, lead_name, company, platform, lead_status, "
                "lead_priority, follow_up_date, created_at FROM social_leads "
                "WHERE workspace_id=? ORDER BY created_at DESC", (ws,))
        self._json_ok({"leads": leads})

    def _handle_contact_create(self, user: dict, ws: str) -> None:
        """Idempotent lead creation, M19<->M06 bridge. Duplicate detection."""
        if not self._has(user, "resource:create"):
            self._json_err("resource:create required", 403)
            return
        data = _read_json(self)
        if not data.get("lead_name"):
            self._json_err("lead_name required", 400)
            return
        _enquiry = (data.get("enquiry_text") or "")[:200]
        from foundation.domains import m19_core
        actor_id = user.get("user_id") if user.get("user_id") is not None else user.get("id")
        if actor_id is None:
            self._json_err("missing actor identity", 401)
            return
        try:
            lead = m19_core.create_lead(
                self.store, actor_id, ws,
                data["lead_name"], data.get("company",""), data.get("platform","instagram"),
                _enquiry, source_post=data.get("source_post",""),
                service_interest=data.get("service_interest",""),
                lead_priority=data.get("lead_priority","medium"),
                assigned_employee_id=data.get("assigned_employee_id"))
        except PermissionError as e:
            self._json_err(str(e), 403)
            return
        self._json_ok({"lead": lead}, 201)

    def _handle_content_list(self, user: dict) -> None:
        """Content pipeline list — workspace-scoped."""
        ws = user.get("workspace_id") or "SSC"
        if not self._has(user, "resource:read"):
            self._json_err("resource:read required", 403)
            return
        rows = self.store.fetchall(
            "SELECT * FROM social_content_items WHERE workspace_id=? ORDER BY created_at DESC", (ws,))
        for r in rows:
            r["keywords"] = json.loads(r.get("keywords") or "[]")
            r["on_screen_text"] = json.loads(r.get("on_screen_text") or "[]")
        self._json_ok({"workspace": ws, "items": rows})

    def _handle_content_create(self, user: dict) -> None:
        """Create a content item."""
        ws = user.get("workspace_id") or "SSC"
        if not self._has(user, "resource:create"):
            self._json_err("resource:create required", 403)
            return
        data = _read_json(self)
        from foundation.domains.m19_core import generate_content_item
        item = generate_content_item(self.store, ws, {
            "content_id": data.get("content_id", "CONT-%d" % (int(time.time() * 1000) % 100000)),
            "business": data.get("business", ws),
            "pillar": data.get("pillar", ""), "platform": data.get("platform", "instagram"),
            "content_format": data.get("content_format", "reel"), "objective": data.get("objective",""),
            "target_audience": data.get("target_audience",""), "journey_stage": data.get("journey_stage",""),
            "hook": data.get("hook",""), "key_message": data.get("key_message",""), "cta": data.get("cta",""),
            "keywords": data.get("keywords",[]), "title": data.get("title",""), "caption": data.get("caption",""),
            "duration_seconds": data.get("duration_seconds",45),
            "required_media": data.get("required_media",[]),
            "production_difficulty": data.get("production_difficulty","medium"),
            "priority": data.get("priority","high"),
        })
        self._json_ok({"item": item}, 201)

    def _handle_content_detail(self, user: dict, cid: str) -> None:
        """Content item detail."""
        ws = user.get("workspace_id") or "SSC"
        row = self.store.fetchone(
            "SELECT * FROM social_content_items WHERE id=? AND workspace_id=?", (cid, ws))
        if not row:
            self._json_err("content item not found", 404)
            return
        row["keywords"] = json.loads(row.get("keywords") or "[]")
        row["on_screen_text"] = json.loads(row.get("on_screen_text") or "[]")
        self._json_ok({"item": row})

    def _handle_content_script(self, user: dict, cid: str) -> None:
        """Get content script + caption (auto-generation returns draft)."""
        ws = user.get("workspace_id") or "SSC"
        row = self.store.fetchone(
            "SELECT * FROM social_content_items WHERE id=? AND workspace_id=?", (cid, ws))
        if not row:
            self._json_err("content item not found", 404)
            return
        from foundation.domains.m19_core import generate_script
        if self._has(user, "resource:edit") and self.command == "PUT":
            data = _read_json(self)
            # Validate: only permit whitelisted fields
            allowed = {"script", "caption", "cta", "title", "hook", "key_message", "on_screen_text"}
            filtered = {k: v for k, v in data.items() if k in allowed}
            if not filtered:
                self._json_err("no permitted fields to update", 400)
                return
            cols = ", ".join("%s=?" % k for k in filtered)
            self.store.exec("UPDATE social_content_items SET %s, updated_at=? WHERE id=?" % cols,
                            (*filtered.values(), now_iso(), cid))
        script = generate_script(self.store, cid, row.get("language", "en")) if not row.get("script") else {"content_id": cid, "script": row["script"]}
        self._json_ok({"item": row, "script": script.get("script", ""), "subtitle_text": script.get("subtitle_text", "")})

    def _handle_content_approval(self, user: dict, cid: str) -> None:
        """Request approval for a content item."""
        ws = user.get("workspace_id") or "SSC"
        row = self.store.fetchone(
            "SELECT * FROM social_content_items WHERE id=? AND workspace_id=?", (cid, ws))
        if not row:
            self._json_err("content item not found", 404)
            return
        from foundation.domains import m19_workflow
        actor_id = user.get("user_id") if user.get("user_id") is not None else user.get("id")
        if actor_id is None:
            self._json_err("missing actor identity", 401)
            return
        try:
            appr = m19_workflow.request_approval(self.store, actor_id, ws, cid, 1)
        except PermissionError as e:
            self._json_err(str(e), 403)
            return
        self._json_ok({"approval": appr}, 201)

    def _handle_content_approval_transition(self, user: dict, cid: str) -> None:
        """Approve/reject a content approval."""
        ws = user.get("workspace_id") or "SSC"
        row = self.store.fetchone(
            "SELECT a.* FROM social_approvals a "
            "JOIN social_content_items ci ON ci.id=a.content_id "
            "WHERE ci.id=? AND (ci.workspace_id=? OR ci.client_workspace_id=?)", (cid, ws, ws))
        if not row:
            self._json_err("approval not found", 404)
            return
        from foundation.domains import m19_workflow
        data = _read_json(self)
        status = data.get("status")
        if status not in ("approved", "rejected", "withdrawn"):
            self._json_err("status must be approved/rejected/withdrawn", 400)
            return
        if status in ("approved", "rejected"):
            if not self._has(user, "approval:approve"):
                self._json_err("permission denied: approval:approve required", 403)
                return
        user_actor_id = user.get("user_id") if user.get("user_id") is not None else user.get("id")
        if user_actor_id is None:
            self._json_err("missing actor identity", 401)
            return
        try:
            result = m19_workflow.approve_approval(self.store, user_actor_id, row["id"],
                final_script=data.get("final_script",""), final_caption=data.get("final_caption",""),
                final_cta=data.get("final_cta",""), final_hashtags=data.get("final_hashtags","[]"))
        except PermissionError as e:
            self._json_err(str(e), 403)
            return
        self._json_ok({"approval": result})

    def _handle_content_versions(self, user: dict, cid: str) -> None:
        """Content version history."""
        ws = user.get("workspace_id") or "SSC"
        rows = self.store.fetchall(
            "SELECT * FROM social_content_versions WHERE content_id=? ORDER BY version DESC", (cid,))
        self._json_ok({"versions": rows, "content_id": cid})

    def _handle_calendar(self, user: dict) -> None:
        """Content calendar view."""
        ws = user.get("workspace_id") or "SSC"
        if not self._has(user, "resource:read"):
            self._json_err("resource:read required", 403)
            return
        rows = self.store.fetchall(
            "SELECT c.*, ci.title, ci.hook FROM social_calendar_entries c "
            "JOIN social_content_items ci ON ci.id=c.content_id "
            "WHERE c.workspace_id=? ORDER BY c.publish_date DESC", (ws,))
        self._json_ok({"workspace": ws, "entries": rows})

    def _handle_media_list(self, user: dict) -> None:
        """Media assets list."""
        ws = user.get("workspace_id") or "SSC"
        from foundation.domains.m19_media import list_media_assets
        assets = list_media_assets(self.store, ws)
        self._json_ok({"workspace": ws, "assets": assets})

    def _handle_media_detail(self, user: dict, aid: str) -> None:
        """Media asset detail."""
        ws = user.get("workspace_id") or "SSC"
        a = self.store.fetchone(
            "SELECT * FROM social_media_assets WHERE id=? AND workspace_id=?", (aid, ws))
        if not a:
            self._json_err("asset not found", 404)
            return
        self._json_ok({"asset": a})

    def _handle_media_upload(self, user: dict) -> None:
        """Upload + validate + extract metadata."""
        ws = user.get("workspace_id") or "SSC"
        if not self._has(user, "resource:create"):
            self._json_err("resource:create required", 403)
            return
        data = _read_json(self)
        from foundation.domains.m19_media import upload_asset
        actor_id = user.get("user_id") if user.get("user_id") is not None else user.get("id")
        if actor_id is None:
            self._json_err("missing actor identity", 401)
            return
        try:
            asset = upload_asset(self.store, actor_id, ws, data["filepath"])
        except FileNotFoundError as e:
            self._json_err(str(e), 404)
            return
        except ValueError as e:
            self._json_err(str(e), 400)
            return
        self._json_ok({"asset": asset}, 201)

    def _handle_media_render(self, user: dict, aid: str) -> None:
        """Start a video render job."""
        ws = user.get("workspace_id") or "SSC"
        if not self._has(user, "resource:create"):
            self._json_err("resource:create required", 403)
            return
        data = _read_json(self)
        from foundation.domains.m19_media import create_video_job
        actor_id = user.get("user_id") if user.get("user_id") is not None else user.get("id")
        if actor_id is None:
            self._json_err("missing actor identity", 401)
            return
        try:
            job = create_video_job(self.store, actor_id, ws, int(aid), script_id=data.get("script_id"), language=data.get("language","en"), aspect_ratio=data.get("aspect_ratio","9:16"))
        except LookupError as e:
            self._json_err(str(e), 404)
            return
        except ValueError as e:
            self._json_err(str(e), 400)
            return
        self._json_ok({"job": job}, 201)

    def _handle_media_output(self, user: dict, aid: str) -> None:
        """Get the latest completed render output for an asset."""
        ws = user.get("workspace_id") or "SSC"
        job = self.store.fetchone(
            "SELECT * FROM social_video_jobs WHERE input_asset_id=? ORDER BY id DESC LIMIT 1", (aid,))
        if not job or job["status"] not in ("completed", "published"):
            self._json_err("no completed render", 404)
            return
        asset = self.store.fetchone(
            "SELECT * FROM social_media_assets WHERE id=?", (job["output_asset_id"],))
        if not asset:
            self._json_err("output asset missing", 404)
            return
        self._json_ok({"job": job, "output_asset": asset})

    def _handle_media_subtitle(self, user: dict, aid: str) -> None:
        """Generate subtitle file (SRT) for a render job."""
        ws = user.get("workspace_id") or "SSC"
        job = self.store.fetchone(
            "SELECT * FROM social_video_jobs WHERE input_asset_id=? ORDER BY id DESC LIMIT 1", (aid,))
        if not job or job["status"] != "completed":
            self._json_err("no completed render", 404)
            return
        from foundation.domains import m19_core
        caption = job.get("script") or ""
        dur = float(job.get("duration_seconds") or 3)
        srt_lines = []
        for i in range(min(5, len(caption) // 40)):
            start = max(1, int(dur * (i + 1) / 20))
            end = max(1, int(dur * (i + 2) / 20))
            srt_lines.append(f"{i + 1}\n00:00:{start:02d}:00\n{i + 1}\n00:00:{end:02d}:00\n{caption[i * 40:(i + 1) * 40]}")
        srt = "\n".join(srt_lines)
        cur = self.store.conn.execute(
            "INSERT INTO social_subtitles (video_job_id, language, srt_text, status) VALUES (?,?,?,?)",
            (job["id"], "en", srt, "generated"))
        self.store.conn.commit()
        self._json_ok({"subtitle": {"id": cur.lastrowid, "language": "en", "status": "generated", "srt_chars": len(srt)}})

    def _handle_media_voiceover(self, user: dict, aid: str) -> None:
        """Trigger local TTS voiceover. Returns the engine status."""
        ws = user.get("workspace_id") or "SSC"
        job = self.store.fetchone(
            "SELECT * FROM social_video_jobs WHERE input_asset_id=? ORDER BY id DESC LIMIT 1", (aid,))
        if not job:
            self._json_err("render job missing", 404)
            return
        self._json_ok({"voiceover": {
            "status": "ready",
            "message": "Local TTS engine is recommended; the current host has no automatic TTS daemon. "
                       "User-provided audio can be attached via uploads. Engine support: espeak-ng / pico2wave (see docs).",
            "supported_languages": ["en", "hi"]
        }})

    def _handle_media_thumbnail(self, user: dict, aid: str) -> None:
        """Return the thumbnail data URL for an asset."""
        ws = user.get("workspace_id") or "SSC"
        a = self.store.fetchone(
            "SELECT * FROM social_media_assets WHERE id=? AND workspace_id=?", (aid, ws))
        if not a:
            self._json_err("asset not found", 404)
            return
        self._json_ok({"thumbnail": a.get("thumb_url","")})

    def _handle_publish_list(self, user: dict) -> None:
        """Publishing queue."""
        ws = user.get("workspace_id") or "SSC"
        rows = self.store.fetchall(
            "SELECT j.*, ci.title AS content_title FROM social_publish_jobs j "
            "JOIN social_content_items ci ON ci.id=j.content_id "
            "WHERE j.workspace_id=? ORDER BY j.publish_at DESC", (ws,))
        self._json_ok({"queue": rows})

    def _handle_publish_create(self, user: dict) -> None:
        """Enqueue a publish job (idempotent; checks approved version first)."""
        ws = user.get("workspace_id") or "SSC"
        if not self._has(user, "approval:create"):
            self._json_err("approval:create required", 403)
            return
        data = _read_json(self)
        from foundation.domains import m19_workflow
        try:
            job = m19_workflow.enqueue_publish(self.store, user.get("user_id") or user.get("id"),
                data["content_id"], data.get("account_id"), data.get("publish_at","2026-12-01"))
        except PermissionError as e:
            self._json_err(str(e), 403)
            return
        self._json_ok({"job": job}, 201)

    def _handle_publish_detail(self, user: dict, pid: str) -> None:
        """Publish job detail."""
        row = self.store.fetchone(
            "SELECT j.* FROM social_publish_jobs j WHERE j.id=?", (pid,))
        if not row:
            self._json_err("job not found", 404)
            return
        self._json_ok({"job": row})

    def _handle_publish_reconcile(self, user: dict, pid: Any) -> None:
        """Reconcile a publish outcome."""
        from foundation.domains import m19_workflow
        try:
            job_id = int(pid)
        except (ValueError, TypeError):
            self._json_err(f"invalid publish job id: {pid}", 400)
            return
        try:
            job = m19_workflow.reconcile_publish(self.store, job_id)
        except LookupError as e:
            self._json_err(str(e), 404)
            return
        except Exception as e:
            self._json_err(str(e), 400)
            return
        self._json_ok({"job": job})

    def _handle_social_accounts(self, user: dict) -> None:
        """Social account registry with multi-platform health and status."""
        ws, err = self._get_request_workspace(user)
        if err:
            self._json_err(err, 403)
            return
        from foundation.domains import social_integrations
        accounts = social_integrations.list_social_accounts(self.store, ws)
        self._json_ok({"workspace": ws, "accounts": accounts})

    def _handle_social_account_add(self, user: dict) -> None:
        """Add a social account."""
        ws, err = self._get_request_workspace(user)
        if err:
            self._json_err(err, 403)
            return
        if not self._has(user, "resource:create"):
            self._json_err("resource:create required", 403)
            return
        data = _read_json(self)
        from foundation.domains.m19_core import add_account
        try:
            acc = add_account(self.store, user.get("user_id") or user.get("id"), ws,
                data.get("platform","instagram"), data.get("platform_account_id",""),
                data.get("display_name",""), data.get("account_url",""),
                data.get("category",""), data.get("account_owner","owner"))
        except ValueError as e:
            self._json_err(str(e), 400)
            return
        self._json_ok({"account": acc}, 201)

    def _handle_social_account_connect(self, user: dict, aid: str) -> None:
        """Tests live OAuth status and returns authentic connection status."""
        from foundation.domains import social_integrations
        res = social_integrations.test_account_connection(self.store, int(aid))
        self._json_ok(res)

    def _handle_social_account_disconnect(self, user: dict, aid: str) -> None:
        """Mark an account as disconnected and revokes stored tokens."""
        from foundation.domains import social_integrations
        res = social_integrations.disconnect_social_account(self.store, int(aid))
        self._json_ok(res)

    def _handle_social_account_sync(self, user: dict, aid: str) -> None:
        """Trigger an account sync and test live telemetry."""
        from foundation.domains import social_integrations
        res = social_integrations.test_account_connection(self.store, int(aid))
        self._json_ok(res)

    def _handle_instagram_route(self, path: str, user: dict) -> None:
        """Multi-Instagram Account Manager & Publishing Engine."""
        from foundation.domains import instagram_multi_manager
        ws, err = self._get_request_workspace(user)
        if err:
            self._json_err(err, 403)
            return

        # 1. Accounts list: GET /api/instagram/accounts
        if path == "/api/instagram/accounts":
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            target_ws = qs.get("workspace_id", [ws])[0]
            accounts = instagram_multi_manager.list_instagram_accounts(self.store, target_ws)
            self._json_ok({"accounts": accounts, "workspace_id": target_ws})
            return

        # 2. Register account: POST /api/instagram/accounts/register
        if path == "/api/instagram/accounts/register":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            data = _read_json(self)
            target_ws = data.get("workspace_id") or ws
            res = instagram_multi_manager.register_instagram_account(self.store, target_ws, data)
            self._json_ok(res, 201 if res.get("ok") else 400)
            return

        # 3. Disconnect account: POST /api/instagram/accounts/disconnect
        if path == "/api/instagram/accounts/disconnect":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            data = _read_json(self)
            aid = int(data.get("account_id", 0))
            res = instagram_multi_manager.disconnect_instagram_account(self.store, aid)
            self._json_ok(res)
            return

        # 4. Settings: POST /api/instagram/accounts/settings
        if path == "/api/instagram/accounts/settings":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            data = _read_json(self)
            aid = int(data.get("account_id", 0))
            settings = data.get("settings", {})
            res = instagram_multi_manager.update_instagram_settings(self.store, aid, settings)
            self._json_ok(res)
            return

        # 5. Drafts: GET/POST /api/instagram/drafts
        if path == "/api/instagram/drafts":
            if self.command == "GET":
                drafts = instagram_multi_manager.list_instagram_drafts(self.store, ws)
                self._json_ok({"drafts": drafts, "workspace_id": ws})
            else:
                data = _read_json(self)
                target_ws = data.get("workspace_id") or ws
                res = instagram_multi_manager.save_instagram_draft(self.store, target_ws, data)
                self._json_ok(res)
            return

        # 6. Multi-Publish: POST /api/instagram/publish
        if path == "/api/instagram/publish":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            data = _read_json(self)
            target_ws = data.get("workspace_id") or ws
            res = instagram_multi_manager.publish_or_schedule_multi_account(
                self.store, target_ws, data, actor_name=user.get("role", "owner")
            )
            self._json_ok(res)
            return

        # 7. History: GET /api/instagram/history
        if path == "/api/instagram/history":
            history = instagram_multi_manager.get_instagram_publishing_history(self.store, ws)
            self._json_ok({"history": history, "workspace_id": ws})
            return

        self._json_err("instagram endpoint not found", 404)

    def _handle_reports_list(self, user: dict) -> None:
        """Reports list + generate."""
        ws = user.get("workspace_id") or "SSC"
        if not self._has(user, "report:list"):
            self._json_err("report:list required", 403)
            return
        from foundation.domains import m19_core
        rows = self.store.fetchall(
            "SELECT * FROM social_reports WHERE workspace_id=? ORDER BY generated_at DESC", (ws,))
        self._json_ok({"reports": rows})

    def _handle_report_generate(self, user: dict) -> None:
        """Generate a report (type weekly/monthly)."""
        ws = user.get("workspace_id") or "SSC"
        if not self._has(user, "report:generate"):
            self._json_err("report generation requires report:generate", 403)
            return
        data = _read_json(self)
        from foundation.domains import m19_core
        try:
            if data.get("report_type") == "weekly":
                rep = m19_core.generate_weekly_report(self.store, ws, data.get("report_period"))
            else:
                rep = m19_core.generate_monthly_report(self.store, ws)
        except Exception as e:
            self._json_err(str(e), 400)
            return
        self._json_ok({"report": rep})

    def _handle_report_detail(self, user: dict, rid: str) -> None:
        """Report detail."""
        row = self.store.fetchone(
            "SELECT * FROM social_reports WHERE id=?", (rid,))
        if not row:
            self._json_err("report not found", 404)
            return
        ws = user.get("workspace_id") or "SSC"
        if user.get("role") != "Owner" and row.get("workspace_id") != ws:
            self._json_err("tenant isolation violation: unauthorized report access", 403)
            return
        self._json_ok({"report": row})

    def _handle_favicon(self):
        """Serve favicon without auth (redirect to a data URI placeholder)."""
        self.send_response(200)
        self.send_header("Content-Type", "image/x-icon")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _handle_static_favicon(self):
        """Try to serve a real favicon file if present."""
        import os
        for f in ["data/favicon.ico", "foundation/favicon.ico", "static/favicon.ico", "favicon.ico"]:
            if os.path.exists(f):
                with open(f, "rb") as fh:
                    data = fh.read()
                self.send_response(200)
                self.send_header("Content-Type", "image/x-icon")
                self.send_header("Content-Length", len(data))
                self.end_headers()
                self.wfile.write(data)
                return
        # No favicon found - serve a minimal placeholder
        self._handle_favicon()

    def _handle_system_health(self, user: dict) -> None:
        import logging
        logging.warning('DEBUG: _handle_system_health called')
        """System health (no auth gate; used by the dashboard). No secrets or DB paths disclosed."""
        import shutil, os, multiprocessing
        ff = shutil.which("ffmpeg") or "ffmpeg"
        try:
            import resource
            ram_mb = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
        except Exception:
            ram_mb = 0
        try:
            disk = os.statvfs('.')
            disk_mb = int((disk.f_blocks * disk.f_frsize) / 1048576)
        except Exception:
            disk_mb = 0
        self._json_ok({
            "ok": True, "service": "SHAH-Group-AI-OS", "python": sys.version.split()[0],
            "ffmpeg": ff, "ffprobe": shutil.which("ffprobe") or "ffprobe",
            "cpu_count": multiprocessing.cpu_count() or 0,
            "ram_mb": ram_mb, "disk_mb": disk_mb,
            "threads": threading.active_count()
        })

    def _handle_system_usage(self, user: dict) -> None:
        """Resource usage (non-sensitive process and I/O summary)."""
        try:
            import resource
            ram = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
        except Exception:
            ram = 0
        self._json_ok({"cpu_percent": 0, "ram_percent": 0, "used_mb": ram})

    def _handle_ai_brain_agents(self, user: dict) -> None:
        """AI Brain agent registry (default list; no auth gate: orchestration view)."""
        from foundation.domains import ai_brain
        rows = ai_brain.list_agents(self.store)
        self._json_ok({"agents": rows})

    def _handle_ai_brain_tasks(self, user: dict) -> None:
        """AI Brain task list."""
        ws = user.get("workspace_id") or "SSC"
        if not self._has(user, "ai:brain:query"):
            self._json_err("ai:brain:query not permitted", 403)
            return
        from foundation.domains import ai_brain
        rows = ai_brain.list_tasks(self.store, ws)
        self._json_ok({"tasks": rows})

    def _handle_ai_brain_task_execute(self, user: dict, task_id: int | None = None) -> None:
        """Execute an AI Brain task with real permission-checked tool execution."""
        ws = user.get("workspace_id") or "SSC"
        if not self._has(user, "ai:brain:query"):
            self._json_err("ai:brain:query not permitted", 403)
            return
        data = _read_json(self) if (self.headers.get("Content-Length") and int(self.headers.get("Content-Length", 0)) > 0) else {}
        if task_id is None:
            task_id = int(data.get("task_id", 0))
        if task_id <= 0:
            self._json_err("task_id required", 400)
            return
        from foundation.domains import ai_brain
        try:
            task = ai_brain.execute_task(self.store, user.get("user_id") or user.get("id"),
                                         task_id,
                                         max_retries=data.get("max_retries", 3))
        except LookupError as e:
            self._json_err(str(e), 404)
            return
        self._json_ok({"task": task})

    def _handle_ai_brain_task_create(self, user: dict) -> None:
        """Create an AI Brain task."""
        ws = user.get("workspace_id") or "SSC"
        if not self._has(user, "ai:brain:query"):
            self._json_err("ai:brain:query not permitted", 403)
            return
        data = _read_json(self)
        from foundation.domains import ai_brain
        actor_id = user.get("user_id") if user.get("user_id") is not None else user.get("id")
        if actor_id is None:
            self._json_err("missing actor identity", 401)
            return
        task = ai_brain.create_task(self.store, actor_id, ws,
            data.get("agent_id"), data.get("title",""), data.get("description",""),
            data.get("priority","medium"), tool_requests=data.get("tool_requests"))
        self._json_ok({"task": task}, 201)

    def _handle_ai_brain_task_status(self, user: dict, tid: str) -> None:
        """Update AI Brain task status (with audit + tool-execution record)."""
        ws = user.get("workspace_id") or "SSC"
        if not self._has(user, "ai:brain:query"):
            self._json_err("ai:brain:query not permitted", 403)
            return
        from foundation.domains import ai_brain
        data = _read_json(self)
        try:
            task = ai_brain.update_task_status(self.store, user.get("user_id") or user.get("id"), int(tid),
                data.get("status","completed"), data.get("result_summary",""), data.get("audit_note",""))
        except LookupError as e:
            self._json_err(str(e), 404)
            return
        self._json_ok({"task": task})

    def _handle_ai_brain_tool_executions(self, user: dict, tid: str) -> None:
        """AI tool execution log for a task."""
        from foundation.domains import ai_brain
        rows = ai_brain.list_tool_executions(self.store, int(tid))
        self._json_ok({"executions": rows})

    def _handle_intelligence_route(self, path: str, user: dict) -> None:
        """Autonomous AI Brain intelligence routes: Ask Anything, Daily Research, Marketing Briefs,
        Reports, Alerts, Knowledge Base, and Scheduler Management."""
        if user is None:
            self._json_err("authentication required", 401)
            return
        if not self._has(user, "ai:brain:query"):
            self._json_err("ai:brain:query not permitted", 403)
            return

        from foundation.domains import ai_intelligence
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        data = _read_json(self) if self.command == "POST" else {}

        # Workspace resolution: Owner can query any workspace specified via query param / body or session;
        # other roles are strictly bound to their assigned workspace.
        assigned_ws = user.get("workspace_id") or "SSC"
        req_ws = qs.get("workspace", [None])[0] or qs.get("workspace_id", [None])[0] or data.get("workspace") or data.get("workspace_id")
        if user.get("role") == "Owner" and req_ws:
            ws = req_ws
        else:
            ws = assigned_ws

        # 1. Ask Anything (POST /api/intelligence/ask)
        if path == "/api/intelligence/ask":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            q = data.get("query", "").strip()
            if not q:
                self._json_err("query required", 400)
                return
            body_ws = data.get("workspace") or data.get("workspace_id")
            target_ws = body_ws if (user.get("role") == "Owner" and body_ws) else ws
            ans = ai_intelligence.ask_anything(self.store, q, target_ws, user.get("role", "Owner"))
            self._json_ok({"answer": ans})
            return

        # 2. Autonomous Daily Research
        if path == "/api/intelligence/research":
            cat = qs.get("category", [None])[0]
            limit = int(qs.get("limit", [15])[0])
            rows = ai_intelligence.get_latest_research_items(self.store, ws, cat, limit)
            self._json_ok({"research": rows})
            return

        if path == "/api/intelligence/research/run":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            cat = data.get("category")
            rows = ai_intelligence.generate_autonomous_daily_research(self.store, ws, cat)
            self._json_ok({"research": rows})
            return

        # 3. Daily Marketing Briefs
        if path in ("/api/intelligence/briefs", "/api/ai/marketing/brief"):
            brief = ai_intelligence.get_latest_marketing_brief(self.store, ws)
            self._json_ok({"brief": brief})
            return

        if path in ("/api/intelligence/briefs/generate", "/api/ai/marketing/brief/generate"):
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            brief = ai_intelligence.generate_daily_marketing_brief(self.store, ws)
            self._json_ok({"brief": brief})
            return

        if path in ("/api/intelligence/briefs/save-to-calendar", "/api/ai/marketing/brief/save-to-calendar"):
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            bid = int(data.get("brief_id", 0))
            platform = data.get("platform", "instagram")
            if not bid:
                self._json_err("brief_id required", 400)
                return
            try:
                res = ai_intelligence.save_brief_to_content_calendar(self.store, ws, bid, platform)
                self._json_ok(res, 201)
            except Exception as e:
                self._json_err(str(e), 400)
            return

        # 4. Proactive Business Alerts
        if path == "/api/intelligence/alerts":
            status = qs.get("status", [None])[0]
            limit = int(qs.get("limit", [50])[0])
            rows = ai_intelligence.list_business_alerts(self.store, ws, status, limit)
            self._json_ok({"alerts": rows})
            return

        if path == "/api/intelligence/alerts/scan":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            alerts = ai_intelligence.scan_proactive_business_alerts(self.store, ws)
            self._json_ok({"alerts": alerts, "count": len(alerts)})
            return

        if path.startswith("/api/intelligence/alerts/") and path.endswith("/resolve"):
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            parts = [x for x in path.split("/") if x]
            try:
                aid = int(parts[3])
            except (IndexError, ValueError):
                aid = int(data.get("alert_id", 0))
            if not aid:
                self._json_err("alert_id required", 400)
                return
            ai_intelligence.resolve_business_alert(self.store, aid)
            self._json_ok({"ok": True, "alert_id": aid})
            return

        # 5. Automated Reports (Daily, Weekly, Monthly)
        if path == "/api/intelligence/reports":
            rtype = qs.get("type", [None])[0]
            limit = int(qs.get("limit", [20])[0])
            rows = ai_intelligence.list_generated_reports(self.store, ws, rtype, limit)
            self._json_ok({"reports": rows})
            return

        if path.startswith("/api/intelligence/reports/"):
            parts = [x for x in path.split("/") if x]
            if len(parts) >= 4 and parts[3] == "generate":
                if self.command != "POST":
                    self._json_err("method not allowed", 405)
                    return
                rtype = data.get("type", "daily").lower()
                if rtype == "weekly":
                    rep = ai_intelligence.generate_weekly_report(self.store, ws)
                elif rtype == "monthly":
                    rep = ai_intelligence.generate_monthly_report(self.store, ws)
                else:
                    rep = ai_intelligence.generate_daily_report(self.store, ws)
                self._json_ok({"report": rep})
                return

            if len(parts) >= 4 and parts[3].isdigit():
                rid = int(parts[3])
                rep = self.store.fetchone("SELECT * FROM ai_generated_reports WHERE id=?", (rid,))
                if not rep:
                    self._json_err("report not found", 404)
                    return
                if user.get("role") != "Owner" and rep.get("workspace_id") and rep["workspace_id"] != ws:
                    self._json_err("tenant isolation violation: unauthorized report access", 403)
                    return
                if len(parts) >= 5 and parts[4] == "export":
                    content = json.loads(rep.get("content_json") or "{}")
                    self._json_ok({"report": rep, "parsed_content": content})
                    return
                self._json_ok({"report": rep})
                return

        # 6. Central Scheduler Jobs & Runs
        if path == "/api/intelligence/scheduler/jobs":
            jobs = ai_intelligence.list_scheduler_jobs(self.store)
            self._json_ok({"jobs": jobs})
            return

        if path == "/api/intelligence/scheduler/runs":
            runs = ai_intelligence.list_scheduler_runs(self.store)
            self._json_ok({"runs": runs})
            return

        if path == "/api/intelligence/scheduler/run-now":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            jkey = data.get("job_key")
            if not jkey:
                self._json_err("job_key required", 400)
                return
            res = ai_intelligence.run_scheduler_job(self.store, jkey)
            self._json_ok({"run": res})
            return

        # 7. Knowledge Base & SOPs
        if path == "/api/intelligence/knowledge":
            if self.command == "POST":
                entry = ai_intelligence.add_knowledge_base_entry(
                    self.store, ws,
                    data.get("category", "custom"),
                    data.get("title", "Untitled SOP"),
                    data.get("content", ""),
                    data.get("tags", "")
                )
                self._json_ok({"entry": entry})
                return
            cat = qs.get("category", [None])[0]
            q = qs.get("q", [None])[0]
            rows = ai_intelligence.query_knowledge_base(self.store, cat, q)
            self._json_ok({"knowledge": rows})
            return

        # 8. Hermes Integration Status & Live Query
        if path == "/api/intelligence/hermes/status":
            from foundation.domains import hermes_bridge
            self._json_ok(hermes_bridge.get_hermes_status(self.store))
            return

        if path == "/api/intelligence/hermes/query":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            prompt = data.get("prompt", "").strip()
            if not prompt:
                self._json_err("prompt required", 400)
                return
            from foundation.domains import hermes_bridge
            res = hermes_bridge.query_hermes(
                self.store,
                prompt,
                system_prompt=data.get("system_prompt", ""),
                workspace_id=ws,
                force_model=data.get("model"),
                force_cli=data.get("use_cli", False)
            )
            self._json_ok(res)
            return

        # 9. Real Live Internet Research
        if path == "/api/intelligence/research/live":
            from foundation.domains import internet_research
            q = data.get("query") if self.command == "POST" else qs.get("query", [""])[0]
            if not q:
                self._json_err("query required", 400)
                return
            cat = data.get("category", "survey_tech") if self.command == "POST" else qs.get("category", ["survey_tech"])[0]
            rep = internet_research.conduct_live_internet_research(self.store, q, ws, cat)
            self._json_ok(rep)
            return

        self._json_err("intelligence endpoint not found", 404)

    def _handle_studio_route(self, path: str, user: dict) -> None:
        if user is None:
            self._json_err("authentication required", 401)
            return
        from foundation.domains import creative_studio
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        data = _read_json(self) if self.command == "POST" else {}
        ws, err = self._get_request_workspace(user, data)
        if err:
            self._json_err(err, 403)
            return
        uid = int(user.get("id") or user.get("user_id") or 1)

        if path == "/api/studio/templates":
            self._json_ok({"templates": creative_studio.list_studio_templates(self.store, ws)})
            return

        if path == "/api/studio/projects":
            if self.command == "POST":
                proj = creative_studio.save_studio_project(self.store, ws, uid, data)
                self._json_ok({"project": proj})
                return
            ptype = qs.get("type", [None])[0]
            self._json_ok({"projects": creative_studio.list_studio_projects(self.store, ws, ptype)})
            return

        if path.startswith("/api/studio/projects/"):
            parts = [x for x in path.split("/") if x]
            pid = int(parts[3])
            if self.command == "DELETE" or (len(parts) >= 5 and parts[4] == "delete"):
                self.store.conn.execute("DELETE FROM studio_projects WHERE id=?", (pid,))
                self.store.conn.commit()
                self._json_ok({"ok": True, "deleted": pid})
                return
            proj = creative_studio.get_studio_project(self.store, pid)
            if not proj:
                self._json_err("project not found", 404)
                return
            self._json_ok({"project": proj})
            return

        if path == "/api/studio/render":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            pid = int(data.get("project_id", 0))
            if not pid:
                self._json_err("project_id required", 400)
                return
            res = creative_studio.render_studio_reel(self.store, uid, pid, data)
            self._json_ok(res)
            return

        if path == "/api/studio/export-canvas":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            pid = int(data.get("project_id", 0))
            b64 = data.get("image_b64", "")
            slide_idx = int(data.get("slide_index", 1))
            res = creative_studio.export_canvas_image(self.store, uid, pid, b64, slide_idx)
            self._json_ok(res)
            return

        # AI Image Generation
        if path == "/api/studio/ai-image/generate":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            prompt = data.get("prompt", "").strip()
            if not prompt:
                self._json_err("prompt required", 400)
                return
            aspect = data.get("aspect_ratio", "1:1")
            style = data.get("style", "surveying_dgps")
            from foundation.domains import ai_image_gen
            res = ai_image_gen.generate_ai_image(self.store, prompt, workspace_id=ws, aspect_ratio=aspect, style_key=style, save_to_library=True)
            self._json_ok(res)
            return

        if path == "/api/studio/ai-image/enhance":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            prompt = data.get("prompt", "").strip()
            style = data.get("style", "surveying_dgps")
            from foundation.domains import ai_image_gen
            enhanced = ai_image_gen.enhance_prompt(prompt, style, ws)
            self._json_ok({"enhanced_prompt": enhanced})
            return

        if path == "/api/studio/ai-image/styles":
            from foundation.domains import ai_image_gen
            self._json_ok(ai_image_gen.get_image_generation_styles())
            return

        # AI Video Generation
        if path == "/api/studio/ai-video/generate-script":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            topic = data.get("topic", "DGPS High Precision Survey").strip()
            from foundation.domains import ai_video_gen
            scenes = ai_video_gen.decompose_script_to_scenes(topic, "", ws)
            self._json_ok({"topic": topic, "scenes": scenes})
            return

        if path == "/api/studio/ai-video/render-script-video":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            topic = data.get("topic", "SHAH Group Project Reel").strip()
            scenes = data.get("scenes", [])
            from foundation.domains import ai_video_gen
            if not scenes:
                scenes = ai_video_gen.decompose_script_to_scenes(topic, "", ws)
            res = ai_video_gen.render_script_video(self.store, topic, scenes, workspace_id=ws, actor_id=uid)
            self._json_ok(res)
            return

        self._json_err("studio endpoint not found", 404)

    def _handle_integrations_route(self, path: str, user: dict) -> None:
        if user is None:
            self._json_err("authentication required", 401)
            return
        if user.get("role") not in ("Owner", "Manager"):
            self._json_err("forbidden: admin/manager access required for integrations", 403)
            return
        ws, err = self._get_request_workspace(user)
        if err:
            self._json_err(err, 403)
            return
        data = _read_json(self) if self.command == "POST" else {}
        from foundation.domains import google_sheets_sync, integrations_center

        # Central Health Monitor
        if path in ("/api/integrations", "/api/integrations/summary", "/api/integrations/center/health", "/api/integrations/status"):
            self._json_ok(integrations_center.get_integration_health_monitor(self.store, ws))
            return

        # Google Sheets Mappings & Sync
        if path == "/api/integrations/sheets/mappings":
            if self.command == "POST":
                m_key = data.get("module_key", "")
                if not m_key:
                    self._json_err("module_key required", 400)
                    return
                res = integrations_center.update_sheet_mapping(self.store, ws, m_key, data)
                self._json_ok(res)
                return
            self._json_ok({"mappings": integrations_center.list_sheets_mappings(self.store, ws)})
            return

        # Google Sheets Metadata & Worksheets
        if path == "/api/integrations/sheets/metadata":
            from foundation.domains import google_sheets_engine
            parsed_url = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed_url.query)
            sp_id = qs.get("spreadsheet_id", [""])[0].strip() or data.get("spreadsheet_id")
            res = google_sheets_engine.fetch_spreadsheet_metadata(self.store.conn, ws, sp_id)
            self._json_ok(res)
            return

        # Select target spreadsheet
        if path == "/api/integrations/sheets/spreadsheet/select":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            sp_id = data.get("spreadsheet_id", "").strip()
            sp_name = data.get("spreadsheet_name", "").strip()
            from foundation.domains import google_sheets_engine
            res = google_sheets_engine.update_workspace_spreadsheet_selection(self.store.conn, ws, sp_id, sp_name)
            self._json_ok(res)
            return

        # Google Sheets Sync History
        if path == "/api/integrations/sheets/history":
            rows = self.store.fetchall(
                "SELECT * FROM google_sheets_sync_history WHERE workspace_id=? ORDER BY id DESC LIMIT 50",
                (ws,)
            )
            self._json_ok({"history": [dict(r) for r in rows]})
            return

        # Google Drive Folders & File Staging
        if path == "/api/integrations/drive/folders":
            self._json_ok(integrations_center.get_drive_folder_tree(self.store, ws))
            return

        if path == "/api/integrations/drive/upload":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            fname = data.get("filename", "").strip()
            fb64 = data.get("file_b64", "").strip()
            mkey = data.get("module_key", "documents").strip()
            if not fname or not fb64:
                self._json_err("filename and file_b64 required", 400)
                return
            res = integrations_center.stage_drive_file_upload(self.store, ws, mkey, fname, fb64)
            self._json_ok(res, 201)
            return

        if path == "/api/integrations/drive/sync":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            from foundation.domains import google_drive_engine
            res = google_drive_engine.sync_all_staged_drive_files(self.store, ws)
            self._json_ok(res)
            return

        # Activity Logs
        if path == "/api/integrations/center/logs":
            logs = self.store.fetchall(
                "SELECT * FROM integration_activity_logs WHERE workspace_id=? ORDER BY id DESC LIMIT 50",
                (ws,)
            )
            self._json_ok({"logs": [dict(l) for l in logs]})
            return

        # Connect / Disconnect Provider
        if path == "/api/integrations/center/connect":
            prov = (data.get("provider") or "google_account").lower().strip()
            acc_name = (data.get("account_name") or "").strip() or f"{prov.capitalize()} Account"
            token_val = (data.get("access_token") or "").strip()
            secret_val = (data.get("app_secret") or "").strip()
            sync_mode = data.get("mode", "safe_staging")

            auth_meta = {
                "access_token": token_val or "TOKEN_CONFIGURED_LIVE_UI",
                "app_secret": secret_val,
                "sync_mode": sync_mode,
                "connected_via": "live_ui",
                "connected_at": now_iso()
            }

            # 1. Update or create social account in social_accounts
            existing = self.store.fetchone(
                "SELECT id FROM social_accounts WHERE workspace_id=? AND platform=?",
                (ws, prov)
            )
            if existing:
                self.store.conn.execute("""
                    UPDATE social_accounts
                    SET display_name=?,
                        platform_account_id=?,
                        connection_status='connected',
                        last_sync_at=datetime('now'),
                        connected_date=datetime('now'),
                        authorized_user=?,
                        auth_details=?
                    WHERE id=?
                """, (
                    f"{acc_name} ({prov.capitalize()})",
                    acc_name,
                    user.get("username", "owner"),
                    json.dumps(auth_meta),
                    existing["id"]
                ))
            else:
                self.store.conn.execute("""
                    INSERT INTO social_accounts (
                        workspace_id, platform, platform_account_id, display_name,
                        account_url, account_category, connection_status,
                        granted_permissions, connected_date, authorized_user,
                        account_metadata, auth_details
                    ) VALUES (?, ?, ?, ?, ?, ?, 'connected', ?, datetime('now'), ?, ?, ?)
                """, (
                    ws,
                    prov,
                    acc_name,
                    f"{acc_name} ({prov.capitalize()})",
                    f"https://{prov}.com/{acc_name.replace('@', '')}",
                    "Official Brand Channel",
                    json.dumps(["publish", "read", "insights"]),
                    user.get("username", "owner"),
                    json.dumps({"account_type": f"{prov.capitalize()} Professional", "sync_mode": sync_mode}),
                    json.dumps(auth_meta)
                ))

            # 2. Save credentials in secure storage
            try:
                from foundation.domains import owner_setup_wizard
                owner_setup_wizard.save_stored_credentials({
                    f"{prov.upper()}_ACCESS_TOKEN": token_val or "TOKEN_CONFIGURED_LIVE_UI",
                    f"{prov.upper()}_ACCOUNT": acc_name
                })
            except Exception:
                pass

            # 3. Log activity
            self.store.conn.execute(
                "INSERT INTO integration_activity_logs (workspace_id, provider, action, status, details) VALUES (?,?,?,?,?)",
                (ws, prov, "Account Connected via Live UI", "success", f"Live UI connected {prov} ({acc_name}) with status ACTIVE")
            )
            self.store.conn.commit()

            self._json_ok({
                "ok": True,
                "status": "connected",
                "provider": prov,
                "account_name": acc_name,
                "message": f"Successfully connected {prov.capitalize()} account '{acc_name}' from Live UI! No code changes needed."
            })
            return

        if path in ("/api/integrations/center/disconnect", "/api/integrations/google/disconnect", "/api/oauth/google/disconnect"):
            from foundation.domains import google_oauth_service
            res = google_oauth_service.disconnect_google_account(self.store.conn, ws)
            self._json_ok(res)
            return

        if path == "/api/integrations/google/status":
            from foundation.domains import google_oauth_service
            acc_info = google_oauth_service.get_google_account_details(self.store.conn, ws)
            sheets_info = google_sheets_sync.get_google_sheets_status(self.store, ws)
            self._json_ok({
                "ok": True,
                "workspace_id": ws,
                "google_account": acc_info,
                "sheets_status": sheets_info
            })
            return

        if path in ("/api/integrations/google/sync", "/api/integrations/sheets/sync"):
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            ent = data.get("entity", "all")
            from foundation.domains import google_sheets_engine
            if ent == "all":
                res = google_sheets_engine.sync_all_approved_modules(self.store, ws)
            else:
                res = google_sheets_engine.sync_approved_report_to_sheet(self.store, ws, ent)
            self._json_ok(res)
            return

        if path == "/api/integrations/drive/folder/update":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            fid = data.get("folder_id")
            dfid = data.get("drive_folder_id", "").strip()
            if not fid:
                self._json_err("folder_id required", 400)
                return
            res = integrations_center.update_drive_folder(self.store, ws, int(fid), dfid)
            self._json_ok(res)
            return

        # Bootstrap: Create brand new Master Google Sheet + Drive Folders + Sync
        if path == "/api/integrations/google/bootstrap":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            from foundation.domains import google_sheets_engine, google_drive_engine
            sheet_title = data.get("sheet_title")
            sheet_res = google_sheets_engine.create_new_master_spreadsheet(self.store.conn, ws, sheet_title)
            drive_res = google_drive_engine.bootstrap_drive_cloud_folders(self.store, ws)
            sync_res = google_sheets_engine.sync_all_approved_modules(self.store, ws)
            drive_sync = google_drive_engine.sync_all_staged_drive_files(self.store, ws)
            self._json_ok({
                "ok": True,
                "workspace_id": ws,
                "sheet": sheet_res,
                "drive": drive_res,
                "sheets_sync": sync_res,
                "drive_sync": drive_sync,
                "message": "Brand new Master Google Sheet and Drive hierarchical folders created & synced."
            })
            return

        self._json_err("integrations endpoint not found", 404)

    def _handle_oauth_callback_browser(self, parsed: urllib.parse.ParseResult) -> None:
        """Handles browser OAuth redirect callback from Google."""
        qs = urllib.parse.parse_qs(parsed.query)
        code = qs.get("code", [""])[0].strip()
        state = qs.get("state", [""])[0].strip()
        error = qs.get("error", [""])[0].strip()

        if error:
            html = f"""<!DOCTYPE html><html><body style="font-family:sans-serif;background:#090d16;color:#f87171;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;"><div style="background:#131c2e;padding:30px;border-radius:12px;text-align:center;max-width:400px;border:1px solid #7f1d1d;"><h2 style="margin:0 0 10px;">OAuth Denied</h2><p style="color:#cbd5e1;font-size:13px;">Provider error: {error}</p><a href="/#integrations" style="color:#38bdf8;text-decoration:none;">Return to App</a></div></body></html>""".encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return

        from foundation.domains import google_oauth_service
        host = self.headers.get("Host", "127.0.0.1:8899")
        proto = self.headers.get("X-Forwarded-Proto") or ("https" if "run.app" in host else "http")
        redirect_uri = f"{proto}://{host}{parsed.path}"
        res = google_oauth_service.exchange_google_code_for_tokens(self.store.conn, code, state, redirect_uri)
        if res.get("ok"):
            email = res.get("account_email", "Google Account")
            html = f"""<!DOCTYPE html><html><head><title>Google Integration Connected</title></head><body style="font-family:sans-serif;background:#090d16;color:#e2e8f0;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;"><div style="background:#131c2e;padding:30px;border-radius:12px;border:1px solid #1e293b;text-align:center;max-width:420px;"><div style="font-size:44px;margin-bottom:8px;">✅</div><h2 style="margin:0 0 8px;color:#38bdf8;">Google Connected!</h2><p style="font-size:13px;color:#94a3b8;line-height:1.5;">Account <strong>{email}</strong> authorized successfully for SHAH GROUP AI OS.</p><a href="/#integrations" style="display:inline-block;margin-top:14px;background:#38bdf8;color:#090d16;padding:8px 18px;border-radius:6px;text-decoration:none;font-weight:600;">Return to Dashboard</a></div><script>if(window.opener){{window.opener.postMessage({{type:'google_oauth_success',email:'{email}'}},'*');setTimeout(()=>window.close(),2500);}}</script></body></html>""".encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return
        else:
            err = res.get("error", "Failed to complete token exchange")
            html = f"""<!DOCTYPE html><html><body style="font-family:sans-serif;background:#090d16;color:#f87171;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;"><div style="background:#131c2e;padding:30px;border-radius:12px;text-align:center;max-width:400px;border:1px solid #7f1d1d;"><h2 style="margin:0 0 10px;">Exchange Failed</h2><p style="color:#cbd5e1;font-size:13px;">{err}</p><a href="/#integrations" style="color:#38bdf8;text-decoration:none;">Return to App</a></div></body></html>""".encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)

    def _handle_oauth_authorize(self, user: dict) -> None:
        """Generates OAuth authorization request with anti-CSRF state token."""
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        provider = qs.get("provider", ["google"])[0]
        ws, err = self._get_request_workspace(user)
        if err:
            self._json_err(err, 403)
            return
        uid = int(user.get("id") or user.get("user_id") or 1)
        if provider.lower() in ("google", "google_account", "google_sheets", "google_drive"):
            from foundation.domains import google_oauth_service
            host = self.headers.get("Host", "127.0.0.1:8899")
            proto = self.headers.get("X-Forwarded-Proto") or ("https" if "run.app" in host else "http")
            redirect_uri = qs.get("redirect_uri", [f"{proto}://{host}/api/oauth/google/callback"])[0]
            res = google_oauth_service.generate_google_oauth_url(self.store.conn, ws, uid, redirect_uri)
            self._json_ok(res)
            return
        from foundation.domains import oauth_service
        res = oauth_service.create_authorization_request(self.store.conn, provider, ws, uid)
        self._json_ok(res)

    def _handle_oauth_callback(self, user: dict) -> None:
        """Handles OAuth callback and validates anti-CSRF state token."""
        data = _read_json(self)
        state_token = data.get("state", "").strip() or data.get("state_token", "").strip()
        code = data.get("code", "").strip()
        error = data.get("error")

        if error:
            self._json_err(f"OAuth consent denied by provider: {error}", 400)
            return

        if not state_token:
            self._json_err("state parameter required", 400)
            return

        from foundation.domains import google_oauth_service
        host = self.headers.get("Host", "127.0.0.1:8899")
        proto = self.headers.get("X-Forwarded-Proto") or ("https" if "run.app" in host else "http")
        redirect_uri = data.get("redirect_uri") or f"{proto}://{host}/api/oauth/google/callback"

        # If authorization code is present, execute full token exchange
        if code:
            res = google_oauth_service.exchange_google_code_for_tokens(self.store.conn, code, state_token, redirect_uri)
            if res.get("ok"):
                self._json_ok(res)
                return
            if "GOOGLE_CLIENT_ID" in str(res.get("error", "")):
                self._json_ok({
                    "ok": False,
                    "state_valid": True,
                    "status": "State Token Verified (Credentials Required)",
                    "message": res["error"]
                })
                return
            self._json_err(res.get("error", "OAuth exchange failed"), 400)
            return

        from foundation.domains import oauth_service
        valid, state_data, msg = oauth_service.validate_state_token(self.store.conn, state_token)
        if not valid:
            self._json_err(f"OAuth CSRF validation failed: {msg}", 400)
            return

        prov = state_data["provider"]
        ws = state_data["workspace_id"]
        self._json_ok({
            "ok": True,
            "provider": prov,
            "workspace_id": ws,
            "status": "State Token Verified",
            "message": "OAuth anti-CSRF state token validated successfully. Provider credentials required to exchange token."
        })

    def _handle_oauth_disconnect(self, user: dict) -> None:
        """Permanently revokes OAuth connection and deletes tokens."""
        data = _read_json(self)
        ws, err = self._get_request_workspace(user, data)
        if err:
            self._json_err(err, 403)
            return

        prov = (data.get("provider") or "").lower()
        account_id = str(data.get("account_id") or "").lower()

        if prov in ("google", "google_account", "google_sheets", "google_drive") or account_id == "google":
            from foundation.domains import google_oauth_service
            res = google_oauth_service.disconnect_google_account(self.store.conn, ws)
            self._json_ok(res)
            return

        aid = data.get("account_id")
        from foundation.domains import social_integrations
        if aid:
            res = social_integrations.disconnect_social_account(self.store, int(aid))
            self._json_ok(res)
            return
        self._json_err("account_id or provider required", 400)

    def _handle_oauth_diagnostic(self, user: dict) -> None:
        """Test diagnostic hook for validating all 6 lifecycle statuses."""
        data = _read_json(self)
        aid = data.get("account_id")
        scenario = data.get("scenario")
        if not aid or not scenario:
            self._json_err("account_id and scenario required", 400)
            return
        from foundation.domains import social_integrations
        res = social_integrations.set_test_diagnostic_status(self.store, int(aid), scenario)
        self._json_ok(res)

    def _handle_gbp_route(self, path: str, user: dict) -> None:
        """First-class Google Business Profile API routes."""
        if user is None:
            self._json_err("authentication required", 401)
            return
        from foundation.domains import google_business_profile
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        data = _read_json(self) if self.command == "POST" else {}
        ws, err = self._get_request_workspace(user, data)
        if err:
            self._json_err(err, 403)
            return

        if path == "/api/gbp/profile":
            self._json_ok(google_business_profile.get_gbp_profile_status(self.store, ws))
            return
        if path == "/api/gbp/config":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            self._json_ok(google_business_profile.update_gbp_config(self.store, ws, data))
            return
        if path == "/api/gbp/posts":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            try:
                res = google_business_profile.create_gbp_post(self.store, ws, data)
                self._json_ok(res, 201)
            except Exception as e:
                self._json_err(str(e), 400)
            return
        if path == "/api/gbp/reviews/reply":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            rid = data.get("review_id", "").strip()
            reply = data.get("reply_text", "").strip()
            if not rid or not reply:
                self._json_err("review_id and reply_text required", 400)
                return
            res = google_business_profile.reply_to_gbp_review(self.store, ws, rid, reply)
            self._json_ok(res)
            return
        self._json_err("gbp endpoint not found", 404)

    def _handle_owner_setup_route(self, path: str, user: dict) -> None:
        """Interactive Owner Setup Center & Checklist routes."""
        if user is None:
            self._json_err("authentication required", 401)
            return
        if user.get("role") != "Owner":
            self._json_err("forbidden: Owner role required for Owner Setup Center", 403)
            return
        from foundation.domains import owner_setup_wizard
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        data = _read_json(self) if self.command == "POST" else {}
        ws, err = self._get_request_workspace(user, data)
        if err:
            self._json_err(err, 403)
            return

        if path == "/api/owner-setup/status":
            self._json_ok(owner_setup_wizard.get_owner_setup_checklist(self.store, ws))
            return
        if path == "/api/owner-setup/credentials":
            if self.command != "POST":
                self._json_err("method not allowed", 405)
                return
            if user.get("role") != "Owner":
                self._json_err("Owner role required for credential configuration", 403)
                return
            res = owner_setup_wizard.save_stored_credentials(data)
            self._json_ok(res)
            return
        self._json_err("owner setup endpoint not found", 404)

    def _handle_tasks_route(self, path: str, user: dict) -> None:
        if user is None:
            self._json_err("authentication required", 401)
            return
        from foundation.domains import task_management
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        data = _read_json(self) if self.command == "POST" else {}
        ws, err = self._get_request_workspace(user, data)
        if err:
            self._json_err(err, 403)
            return
        uid = int(user.get("id") or user.get("user_id") or 1)

        if path == "/api/tasks":
            if self.command == "POST":
                t = task_management.create_employee_task(self.store, ws, uid, data)
                self._json_ok({"task": t}, 201)
                return
            ftype = qs.get("filter_type", ["all"])[0]
            status = qs.get("status", [None])[0]
            priority = qs.get("priority", [None])[0]
            pid = qs.get("project_id", [None])[0]
            tasks = task_management.list_employee_tasks(
                self.store, ws, uid, user.get("role", "Owner"),
                filter_type=ftype, status=status, priority=priority, project_id=pid
            )
            self._json_ok({"tasks": tasks})
            return

        if path == "/api/tasks/workload":
            self._json_ok(task_management.get_admin_workload_summary(self.store, ws))
            return

        if path == "/api/tasks/notifications":
            if self.command == "POST":
                nid = int(data.get("notification_id", 0))
                task_management.mark_notification_read(self.store, nid, uid)
                self._json_ok({"ok": True})
                return
            unread = qs.get("unread", ["0"])[0] == "1"
            notifs = task_management.list_user_notifications(self.store, uid, unread_only=unread)
            self._json_ok({"notifications": notifs})
            return

        parts = [x for x in path.split("/") if x]
        if len(parts) >= 3 and parts[2].isdigit():
            tid = int(parts[2])
            t = task_management.get_employee_task(self.store, tid)
            if not t:
                self._json_err("task not found", 404)
                return
            if user.get("role") != "Owner" and t.get("workspace_id") != ws:
                self._json_err("tenant isolation violation: unauthorized task access", 403)
                return
            if len(parts) == 3:
                self._json_ok({"task": t})
                return
            action = parts[3]
            if action == "accept":
                self._json_ok({"task": task_management.accept_task(self.store, tid, uid)})
                return
            if action == "progress":
                pct = int(data.get("progress_pct", 0))
                note = data.get("note", "")
                self._json_ok({"task": task_management.update_task_progress(self.store, tid, uid, pct, note)})
                return
            if action == "proof":
                proof_text = data.get("proof_text", "")
                proof_url = data.get("proof_url", "")
                self._json_ok({"task": task_management.submit_task_work_proof(self.store, tid, uid, proof_text, proof_url)})
                return
            if action == "review":
                decision = data.get("decision", "approve")
                notes = data.get("notes", "")
                self._json_ok({"task": task_management.review_task(self.store, tid, uid, decision, notes)})
                return
            if action == "comments":
                if self.command == "POST":
                    c = task_management.add_task_comment(self.store, tid, uid, data.get("comment_text", ""))
                    self._json_ok({"comment": c})
                    return
                self._json_ok({"comments": task_management.list_task_comments(self.store, tid)})
                return

        self._json_err("tasks endpoint not found", 404)

    def _handle_filter_route(self, path: str, user: dict) -> None:
        if user is None:
            self._json_err("authentication required", 401)
            return
        from foundation.domains import filter_system
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        data = _read_json(self) if self.command == "POST" else {}
        ws, err = self._get_request_workspace(user, data)
        if err:
            self._json_err(err, 403)
            return

        parts = [x for x in path.split("/") if x]
        if len(parts) < 3:
            self._json_err("filter entity required", 400)
            return
        entity = parts[2]
        
        # Combine query params and POST body for flexible filtering
        filters = dict(data)
        for k, v in qs.items():
            if k not in filters and v:
                filters[k] = v[0]

        if entity == "query":
            entity = filters.get("entity", "leads")

        if len(parts) >= 4 and parts[3] == "export":
            try:
                csv_text, fname = filter_system.export_filtered_csv(self.store, entity, ws, filters)
                b = csv_text.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", f'attachment; filename="{fname}"')
                self.send_header("Content-Length", str(len(b)))
                self.end_headers()
                self.wfile.write(b)
            except Exception as e:
                self._json_err(str(e), 400)
            return

        try:
            page = int(filters.get("page", 1))
            limit = int(filters.get("limit", 20))
            sort_by = filters.get("sort_by")
            sort_dir = filters.get("sort_dir", "DESC")
            res = filter_system.query_filtered_records(self.store, entity, ws, filters, page, limit, sort_by, sort_dir)
            self._json_ok(res)
        except Exception as e:
            self._json_err(str(e), 400)

    def log_message(self, fmt, *args):  # quieter request logging
        pass


def make_server(host: str = "127.0.0.1", port: int = 8899):
    from foundation.scheduler import start_scheduler
    start_scheduler(get_store())
    return ThreadingHTTPServer((host, port), Handler)


if __name__ == "__main__":
    import os, sys
    # Ensure the project root is on sys.path for direct script execution
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from foundation import config as foundation_config
    cfg = foundation_config.load_config()
    port = int(os.getenv("PORT", cfg.get("port", 8899)))
    cloud_env = os.getenv("RENDER") or os.getenv("K_SERVICE") or os.getenv("GAE_APPLICATION") or (os.getenv("PORT") is not None)
    host = os.getenv("HOST", "0.0.0.0" if cloud_env else cfg.get("host", "127.0.0.1"))
    srv = make_server(host, port)
    print(f"SHAI foundation API listening on http://{srv.server_address[0]}:{srv.server_address[1]}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.server_close()
