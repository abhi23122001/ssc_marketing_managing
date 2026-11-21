"""Business Operations domain: Estimates, Quotations (BOQ), Work Orders, Invoices (GST), Payments, and P&L.

Completes the full operational business pipeline:
Lead -> Client -> Enquiry -> Site Visit -> Estimate -> Quotation -> Work Order -> Project ->
Team Allocation -> Field Work -> QC -> Report -> Invoice -> Payment -> Expense -> Profit -> Closure.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


_BUSINESS_OPS_SCHEMA = """
CREATE TABLE IF NOT EXISTS business_estimates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    lead_id INTEGER,
    client_id INTEGER,
    title TEXT NOT NULL,
    service_type TEXT NOT NULL DEFAULT 'DGPS Survey',
    site_location TEXT NOT NULL DEFAULT '',
    estimated_amount REAL NOT NULL DEFAULT 0,
    scope_of_work TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (lead_id) REFERENCES social_leads(id) ON DELETE SET NULL,
    FOREIGN KEY (client_id) REFERENCES social_client_profiles(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS business_quotations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    quotation_number TEXT UNIQUE NOT NULL,
    client_id INTEGER,
    estimate_id INTEGER,
    project_name TEXT NOT NULL,
    subtotal REAL NOT NULL DEFAULT 0,
    gst_rate REAL NOT NULL DEFAULT 18.0,
    gst_amount REAL NOT NULL DEFAULT 0,
    total_amount REAL NOT NULL DEFAULT 0,
    items_json TEXT NOT NULL DEFAULT '[]',
    validity_days INTEGER NOT NULL DEFAULT 30,
    terms TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES social_client_profiles(id) ON DELETE SET NULL,
    FOREIGN KEY (estimate_id) REFERENCES business_estimates(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS business_work_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    work_order_number TEXT UNIQUE NOT NULL,
    quotation_id INTEGER,
    client_id INTEGER,
    site_id INTEGER,
    title TEXT NOT NULL,
    start_date TEXT NOT NULL DEFAULT '',
    target_completion_date TEXT NOT NULL DEFAULT '',
    total_contract_value REAL NOT NULL DEFAULT 0,
    assigned_team_leader_id INTEGER,
    field_qc_status TEXT NOT NULL DEFAULT 'pending',
    deliverables_status TEXT NOT NULL DEFAULT 'drafting',
    status TEXT NOT NULL DEFAULT 'issued',
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (quotation_id) REFERENCES business_quotations(id) ON DELETE SET NULL,
    FOREIGN KEY (client_id) REFERENCES social_client_profiles(id) ON DELETE SET NULL,
    FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_team_leader_id) REFERENCES employees(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS business_invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    invoice_number TEXT UNIQUE NOT NULL,
    work_order_id INTEGER,
    client_id INTEGER,
    invoice_date TEXT NOT NULL,
    due_date TEXT NOT NULL,
    subtotal REAL NOT NULL DEFAULT 0,
    cgst_amount REAL NOT NULL DEFAULT 0,
    sgst_amount REAL NOT NULL DEFAULT 0,
    igst_amount REAL NOT NULL DEFAULT 0,
    total_tax REAL NOT NULL DEFAULT 0,
    total_amount REAL NOT NULL DEFAULT 0,
    items_json TEXT NOT NULL DEFAULT '[]',
    amount_paid REAL NOT NULL DEFAULT 0,
    payment_status TEXT NOT NULL DEFAULT 'unpaid',
    status TEXT NOT NULL DEFAULT 'issued',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (work_order_id) REFERENCES business_work_orders(id) ON DELETE SET NULL,
    FOREIGN KEY (client_id) REFERENCES social_client_profiles(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS business_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    invoice_id INTEGER NOT NULL,
    payment_date TEXT NOT NULL,
    amount REAL NOT NULL DEFAULT 0,
    payment_mode TEXT NOT NULL DEFAULT 'NEFT/RTGS',
    reference_number TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (invoice_id) REFERENCES business_invoices(id) ON DELETE CASCADE
);
"""


def ensure_business_ops_schema(conn) -> None:
    """Ensure business operations tables exist."""
    conn.executescript(_BUSINESS_OPS_SCHEMA)
    conn.commit()


# ---------------------------------------------------------------------------
# Estimates
# ---------------------------------------------------------------------------
def create_estimate(conn, workspace_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    ensure_business_ops_schema(conn)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO business_estimates (
            workspace_id, lead_id, client_id, title, service_type,
            site_location, estimated_amount, scope_of_work, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            workspace_id,
            data.get("lead_id"),
            data.get("client_id"),
            data.get("title", "Project Survey Estimate"),
            data.get("service_type", "DGPS Survey"),
            data.get("site_location", ""),
            float(data.get("estimated_amount", 0.0)),
            data.get("scope_of_work", ""),
            data.get("status", "draft"),
        ),
    )
    est_id = cur.lastrowid
    conn.commit()
    return get_estimate(conn, est_id)


def list_estimates(conn, workspace_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
    ensure_business_ops_schema(conn)
    query = """
        SELECT e.id, e.workspace_id, e.lead_id, e.client_id, e.title,
               e.service_type, e.site_location, e.estimated_amount,
               e.scope_of_work, e.status, e.created_at,
               COALESCE(c.company_name, l.company, l.lead_name) as client_name
        FROM business_estimates e
        LEFT JOIN social_client_profiles c ON e.client_id = c.id
        LEFT JOIN social_leads l ON e.lead_id = l.id
        WHERE e.workspace_id = ?
    """
    params: List[Any] = [workspace_id]
    if status:
        query += " AND e.status = ?"
        params.append(status)
    query += " ORDER BY e.id DESC"
    
    rows = conn.execute(query, params).fetchall()
    cols = ["id", "workspace_id", "lead_id", "client_id", "title",
            "service_type", "site_location", "estimated_amount",
            "scope_of_work", "status", "created_at", "client_name"]
    return [dict(zip(cols, r)) for r in rows]


def get_estimate(conn, estimate_id: int) -> Optional[Dict[str, Any]]:
    ensure_business_ops_schema(conn)
    query = """
        SELECT e.id, e.workspace_id, e.lead_id, e.client_id, e.title,
               e.service_type, e.site_location, e.estimated_amount,
               e.scope_of_work, e.status, e.created_at,
               COALESCE(c.company_name, l.company, l.lead_name) as client_name
        FROM business_estimates e
        LEFT JOIN social_client_profiles c ON e.client_id = c.id
        LEFT JOIN social_leads l ON e.lead_id = l.id
        WHERE e.id = ?
    """
    row = conn.execute(query, (estimate_id,)).fetchone()
    if not row:
        return None
    cols = ["id", "workspace_id", "lead_id", "client_id", "title",
            "service_type", "site_location", "estimated_amount",
            "scope_of_work", "status", "created_at", "client_name"]
    return dict(zip(cols, row))


def update_estimate_status(conn, estimate_id: int, status: str) -> Optional[Dict[str, Any]]:
    ensure_business_ops_schema(conn)
    conn.execute("UPDATE business_estimates SET status = ? WHERE id = ?", (status, estimate_id))
    conn.commit()
    return get_estimate(conn, estimate_id)


# ---------------------------------------------------------------------------
# Quotations & BOQ
# ---------------------------------------------------------------------------
def _generate_quotation_number(conn, workspace_id: str) -> str:
    year = datetime.now().year
    prefix = f"{workspace_id}-QT-{year}-"
    row = conn.execute(
        "SELECT count(*) FROM business_quotations WHERE quotation_number LIKE ?",
        (f"{prefix}%",)
    ).fetchone()
    count = (row[0] if row else 0) + 1
    return f"{prefix}{count:03d}"


def create_quotation(conn, workspace_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    ensure_business_ops_schema(conn)
    items = data.get("items", [])
    if isinstance(items, str):
        try:
            items = json.loads(items)
        except Exception:
            items = []
            
    # Calculate subtotal from line items or direct input
    subtotal = float(data.get("subtotal", 0.0))
    if items:
        computed_subtotal = 0.0
        for it in items:
            qty = float(it.get("quantity", 1))
            rate = float(it.get("rate", 0))
            amt = it.get("amount")
            if amt is None:
                amt = qty * rate
                it["amount"] = amt
            computed_subtotal += float(amt)
        subtotal = computed_subtotal

    gst_rate = float(data.get("gst_rate", 18.0))
    gst_amount = round(subtotal * (gst_rate / 100.0), 2)
    total_amount = round(subtotal + gst_amount, 2)
    
    q_num = data.get("quotation_number") or _generate_quotation_number(conn, workspace_id)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO business_quotations (
            workspace_id, quotation_number, client_id, estimate_id, project_name,
            subtotal, gst_rate, gst_amount, total_amount, items_json,
            validity_days, terms, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            workspace_id,
            q_num,
            data.get("client_id"),
            data.get("estimate_id"),
            data.get("project_name", "Survey Consultancy Work"),
            subtotal,
            gst_rate,
            gst_amount,
            total_amount,
            json.dumps(items),
            int(data.get("validity_days", 30)),
            data.get("terms", "Payment: 50% Advance, 50% on deliverable submission."),
            data.get("status", "draft"),
        ),
    )
    qid = cur.lastrowid
    conn.commit()
    return get_quotation(conn, qid)


def list_quotations(conn, workspace_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
    ensure_business_ops_schema(conn)
    query = """
        SELECT q.id, q.workspace_id, q.quotation_number, q.client_id, q.estimate_id,
               q.project_name, q.subtotal, q.gst_rate, q.gst_amount, q.total_amount,
               q.items_json, q.validity_days, q.terms, q.status, q.created_at,
               c.company_name as client_name
        FROM business_quotations q
        LEFT JOIN social_client_profiles c ON q.client_id = c.id
        WHERE q.workspace_id = ?
    """
    params: List[Any] = [workspace_id]
    if status:
        query += " AND q.status = ?"
        params.append(status)
    query += " ORDER BY q.id DESC"
    
    rows = conn.execute(query, params).fetchall()
    cols = ["id", "workspace_id", "quotation_number", "client_id", "estimate_id",
            "project_name", "subtotal", "gst_rate", "gst_amount", "total_amount",
            "items_json", "validity_days", "terms", "status", "created_at", "client_name"]
    res = []
    for r in rows:
        d = dict(zip(cols, r))
        try:
            d["items"] = json.loads(d["items_json"])
        except Exception:
            d["items"] = []
        res.append(d)
    return res


def get_quotation(conn, quotation_id: int) -> Optional[Dict[str, Any]]:
    ensure_business_ops_schema(conn)
    query = """
        SELECT q.id, q.workspace_id, q.quotation_number, q.client_id, q.estimate_id,
               q.project_name, q.subtotal, q.gst_rate, q.gst_amount, q.total_amount,
               q.items_json, q.validity_days, q.terms, q.status, q.created_at,
               c.company_name as client_name
        FROM business_quotations q
        LEFT JOIN social_client_profiles c ON q.client_id = c.id
        WHERE q.id = ?
    """
    row = conn.execute(query, (quotation_id,)).fetchone()
    if not row:
        return None
    cols = ["id", "workspace_id", "quotation_number", "client_id", "estimate_id",
            "project_name", "subtotal", "gst_rate", "gst_amount", "total_amount",
            "items_json", "validity_days", "terms", "status", "created_at", "client_name"]
    d = dict(zip(cols, row))
    try:
        d["items"] = json.loads(d["items_json"])
    except Exception:
        d["items"] = []
    return d


def update_quotation_status(conn, quotation_id: int, status: str) -> Optional[Dict[str, Any]]:
    ensure_business_ops_schema(conn)
    conn.execute("UPDATE business_quotations SET status = ? WHERE id = ?", (status, quotation_id))
    conn.commit()
    return get_quotation(conn, quotation_id)


# ---------------------------------------------------------------------------
# Work Orders
# ---------------------------------------------------------------------------
def _generate_wo_number(conn, workspace_id: str) -> str:
    year = datetime.now().year
    prefix = f"{workspace_id}-WO-{year}-"
    row = conn.execute(
        "SELECT count(*) FROM business_work_orders WHERE work_order_number LIKE ?",
        (f"{prefix}%",)
    ).fetchone()
    count = (row[0] if row else 0) + 1
    return f"{prefix}{count:03d}"


def create_work_order(conn, workspace_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    ensure_business_ops_schema(conn)
    wo_num = data.get("work_order_number") or _generate_wo_number(conn, workspace_id)
    qid = data.get("quotation_id")
    
    # Auto-fill from quotation if available
    contract_val = float(data.get("total_contract_value", 0.0))
    cid = data.get("client_id")
    title = data.get("title", "")
    if qid:
        q = get_quotation(conn, qid)
        if q:
            if not contract_val:
                contract_val = float(q.get("total_amount", 0.0))
            if not cid:
                cid = q.get("client_id")
            if not title:
                title = f"WO: {q.get('project_name', 'Survey Contract')}"
            # Mark quotation as accepted / converted
            conn.execute("UPDATE business_quotations SET status = 'converted_to_wo' WHERE id = ?", (qid,))

    if not title:
        title = "Survey Operations Work Order"

    start_date = data.get("start_date") or datetime.now().strftime("%Y-%m-%d")
    target_date = data.get("target_completion_date") or (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO business_work_orders (
            workspace_id, work_order_number, quotation_id, client_id, site_id,
            title, start_date, target_completion_date, total_contract_value,
            assigned_team_leader_id, field_qc_status, deliverables_status,
            status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            workspace_id,
            wo_num,
            qid,
            cid,
            data.get("site_id"),
            title,
            start_date,
            target_date,
            contract_val,
            data.get("assigned_team_leader_id"),
            data.get("field_qc_status", "pending"),
            data.get("deliverables_status", "drafting"),
            data.get("status", "issued"),
            data.get("notes", ""),
        ),
    )
    wo_id = cur.lastrowid
    conn.commit()
    return get_work_order(conn, wo_id)


def list_work_orders(conn, workspace_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
    ensure_business_ops_schema(conn)
    query = """
        SELECT w.id, w.workspace_id, w.work_order_number, w.quotation_id, w.client_id,
               w.site_id, w.title, w.start_date, w.target_completion_date,
               w.total_contract_value, w.assigned_team_leader_id, w.field_qc_status,
               w.deliverables_status, w.status, w.notes, w.created_at,
               c.company_name as client_name,
               s.name as site_name, s.code as site_code,
               e.name as team_leader_name
        FROM business_work_orders w
        LEFT JOIN social_client_profiles c ON w.client_id = c.id
        LEFT JOIN sites s ON w.site_id = s.id
        LEFT JOIN employees e ON w.assigned_team_leader_id = e.id
        WHERE w.workspace_id = ?
    """
    params: List[Any] = [workspace_id]
    if status:
        query += " AND w.status = ?"
        params.append(status)
    query += " ORDER BY w.id DESC"
    
    rows = conn.execute(query, params).fetchall()
    cols = ["id", "workspace_id", "work_order_number", "quotation_id", "client_id",
            "site_id", "title", "start_date", "target_completion_date",
            "total_contract_value", "assigned_team_leader_id", "field_qc_status",
            "deliverables_status", "status", "notes", "created_at",
            "client_name", "site_name", "site_code", "team_leader_name"]
    return [dict(zip(cols, r)) for r in rows]


def get_work_order(conn, work_order_id: int) -> Optional[Dict[str, Any]]:
    ensure_business_ops_schema(conn)
    query = """
        SELECT w.id, w.workspace_id, w.work_order_number, w.quotation_id, w.client_id,
               w.site_id, w.title, w.start_date, w.target_completion_date,
               w.total_contract_value, w.assigned_team_leader_id, w.field_qc_status,
               w.deliverables_status, w.status, w.notes, w.created_at,
               c.company_name as client_name,
               s.name as site_name, s.code as site_code,
               e.name as team_leader_name
        FROM business_work_orders w
        LEFT JOIN social_client_profiles c ON w.client_id = c.id
        LEFT JOIN sites s ON w.site_id = s.id
        LEFT JOIN employees e ON w.assigned_team_leader_id = e.id
        WHERE w.id = ?
    """
    row = conn.execute(query, (work_order_id,)).fetchone()
    if not row:
        return None
    cols = ["id", "workspace_id", "work_order_number", "quotation_id", "client_id",
            "site_id", "title", "start_date", "target_completion_date",
            "total_contract_value", "assigned_team_leader_id", "field_qc_status",
            "deliverables_status", "status", "notes", "created_at",
            "client_name", "site_name", "site_code", "team_leader_name"]
    return dict(zip(cols, row))


def update_work_order_status(conn, work_order_id: int, status: str,
                             field_qc_status: Optional[str] = None,
                             deliverables_status: Optional[str] = None) -> Optional[Dict[str, Any]]:
    ensure_business_ops_schema(conn)
    updates = ["status = ?"]
    params: List[Any] = [status]
    if field_qc_status:
        updates.append("field_qc_status = ?")
        params.append(field_qc_status)
    if deliverables_status:
        updates.append("deliverables_status = ?")
        params.append(deliverables_status)
    params.append(work_order_id)
    
    conn.execute(f"UPDATE business_work_orders SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    return get_work_order(conn, work_order_id)


# ---------------------------------------------------------------------------
# Invoices & GST Tax Engine
# ---------------------------------------------------------------------------
def _generate_invoice_number(conn, workspace_id: str) -> str:
    year = datetime.now().year
    prefix = f"{workspace_id}-INV-{year}-"
    row = conn.execute(
        "SELECT count(*) FROM business_invoices WHERE invoice_number LIKE ?",
        (f"{prefix}%",)
    ).fetchone()
    count = (row[0] if row else 0) + 1
    return f"{prefix}{count:03d}"


def create_invoice(conn, workspace_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    ensure_business_ops_schema(conn)
    inv_num = data.get("invoice_number") or _generate_invoice_number(conn, workspace_id)
    
    wo_id = data.get("work_order_id")
    client_id = data.get("client_id")
    if wo_id and not client_id:
        wo = get_work_order(conn, wo_id)
        if wo:
            client_id = wo.get("client_id")

    items = data.get("items", [])
    if isinstance(items, str):
        try:
            items = json.loads(items)
        except Exception:
            items = []

    subtotal = float(data.get("subtotal", 0.0))
    if items:
        subtotal = sum(float(it.get("amount", float(it.get("rate", 0)) * float(it.get("quantity", 1)))) for it in items)

    # Tax Engine: Intra-State (CGST 9% + SGST 9%) or Inter-State (IGST 18%)
    is_interstate = bool(data.get("is_interstate", False))
    gst_rate = float(data.get("gst_rate", 18.0))
    
    if is_interstate:
        cgst = 0.0
        sgst = 0.0
        igst = round(subtotal * (gst_rate / 100.0), 2)
    else:
        half_rate = gst_rate / 2.0
        cgst = round(subtotal * (half_rate / 100.0), 2)
        sgst = round(subtotal * (half_rate / 100.0), 2)
        igst = 0.0

    total_tax = round(cgst + sgst + igst, 2)
    total_amount = round(subtotal + total_tax, 2)

    inv_date = data.get("invoice_date") or datetime.now().strftime("%Y-%m-%d")
    due_date = data.get("due_date") or (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO business_invoices (
            workspace_id, invoice_number, work_order_id, client_id,
            invoice_date, due_date, subtotal, cgst_amount, sgst_amount,
            igst_amount, total_tax, total_amount, items_json, amount_paid,
            payment_status, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            workspace_id,
            inv_num,
            wo_id,
            client_id,
            inv_date,
            due_date,
            subtotal,
            cgst,
            sgst,
            igst,
            total_tax,
            total_amount,
            json.dumps(items),
            0.0,
            "unpaid",
            data.get("status", "issued"),
        ),
    )
    inv_id = cur.lastrowid
    conn.commit()
    return get_invoice(conn, inv_id)


def list_invoices(conn, workspace_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
    ensure_business_ops_schema(conn)
    query = """
        SELECT i.id, i.workspace_id, i.invoice_number, i.work_order_id, i.client_id,
               i.invoice_date, i.due_date, i.subtotal, i.cgst_amount, i.sgst_amount,
               i.igst_amount, i.total_tax, i.total_amount, i.items_json, i.amount_paid,
               i.payment_status, i.status, i.created_at,
               c.company_name as client_name,
               w.work_order_number, w.title as work_order_title
        FROM business_invoices i
        LEFT JOIN social_client_profiles c ON i.client_id = c.id
        LEFT JOIN business_work_orders w ON i.work_order_id = w.id
        WHERE i.workspace_id = ?
    """
    params: List[Any] = [workspace_id]
    if status:
        query += " AND i.status = ?"
        params.append(status)
    query += " ORDER BY i.id DESC"
    
    rows = conn.execute(query, params).fetchall()
    cols = ["id", "workspace_id", "invoice_number", "work_order_id", "client_id",
            "invoice_date", "due_date", "subtotal", "cgst_amount", "sgst_amount",
            "igst_amount", "total_tax", "total_amount", "items_json", "amount_paid",
            "payment_status", "status", "created_at", "client_name",
            "work_order_number", "work_order_title"]
    res = []
    for r in rows:
        d = dict(zip(cols, r))
        try:
            d["items"] = json.loads(d["items_json"])
        except Exception:
            d["items"] = []
        d["balance_due"] = round(float(d["total_amount"]) - float(d["amount_paid"]), 2)
        res.append(d)
    return res


def get_invoice(conn, invoice_id: int) -> Optional[Dict[str, Any]]:
    ensure_business_ops_schema(conn)
    query = """
        SELECT i.id, i.workspace_id, i.invoice_number, i.work_order_id, i.client_id,
               i.invoice_date, i.due_date, i.subtotal, i.cgst_amount, i.sgst_amount,
               i.igst_amount, i.total_tax, i.total_amount, i.items_json, i.amount_paid,
               i.payment_status, i.status, i.created_at,
               c.company_name as client_name,
               w.work_order_number, w.title as work_order_title
        FROM business_invoices i
        LEFT JOIN social_client_profiles c ON i.client_id = c.id
        LEFT JOIN business_work_orders w ON i.work_order_id = w.id
        WHERE i.id = ?
    """
    row = conn.execute(query, (invoice_id,)).fetchone()
    if not row:
        return None
    cols = ["id", "workspace_id", "invoice_number", "work_order_id", "client_id",
            "invoice_date", "due_date", "subtotal", "cgst_amount", "sgst_amount",
            "igst_amount", "total_tax", "total_amount", "items_json", "amount_paid",
            "payment_status", "status", "created_at", "client_name",
            "work_order_number", "work_order_title"]
    d = dict(zip(cols, row))
    try:
        d["items"] = json.loads(d["items_json"])
    except Exception:
        d["items"] = []
    d["balance_due"] = round(float(d["total_amount"]) - float(d["amount_paid"]), 2)
    d["payments"] = list_payments(conn, d["workspace_id"], invoice_id)
    return d


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------
def record_payment(conn, workspace_id: str, invoice_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    ensure_business_ops_schema(conn)
    amount = float(data.get("amount", 0.0))
    if amount <= 0:
        raise ValueError("Payment amount must be greater than 0")

    p_date = data.get("payment_date") or datetime.now().strftime("%Y-%m-%d")
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO business_payments (
            workspace_id, invoice_id, payment_date, amount, payment_mode, reference_number, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            workspace_id,
            invoice_id,
            p_date,
            amount,
            data.get("payment_mode", "NEFT/RTGS"),
            data.get("reference_number", ""),
            data.get("notes", ""),
        ),
    )
    
    # Recalculate invoice amount_paid and status
    total_paid_row = conn.execute(
        "SELECT SUM(amount) FROM business_payments WHERE invoice_id = ?",
        (invoice_id,)
    ).fetchone()
    total_paid = float(total_paid_row[0] if total_paid_row and total_paid_row[0] else 0.0)

    inv = conn.execute("SELECT total_amount FROM business_invoices WHERE id = ?", (invoice_id,)).fetchone()
    if inv:
        total_inv = float(inv[0])
        if total_paid >= total_inv:
            new_p_status = "paid"
            new_status = "paid"
        elif total_paid > 0:
            new_p_status = "partially_paid"
            new_status = "issued"
        else:
            new_p_status = "unpaid"
            new_status = "issued"
            
        conn.execute(
            "UPDATE business_invoices SET amount_paid = ?, payment_status = ?, status = ? WHERE id = ?",
            (total_paid, new_p_status, new_status, invoice_id),
        )

    conn.commit()
    return get_invoice(conn, invoice_id)


def list_payments(conn, workspace_id: str, invoice_id: Optional[int] = None) -> List[Dict[str, Any]]:
    ensure_business_ops_schema(conn)
    query = """
        SELECT p.id, p.workspace_id, p.invoice_id, p.payment_date, p.amount,
               p.payment_mode, p.reference_number, p.notes, p.created_at,
               i.invoice_number, c.company_name as client_name
        FROM business_payments p
        LEFT JOIN business_invoices i ON p.invoice_id = i.id
        LEFT JOIN social_client_profiles c ON i.client_id = c.id
        WHERE p.workspace_id = ?
    """
    params: List[Any] = [workspace_id]
    if invoice_id:
        query += " AND p.invoice_id = ?"
        params.append(invoice_id)
    query += " ORDER BY p.id DESC"
    
    rows = conn.execute(query, params).fetchall()
    cols = ["id", "workspace_id", "invoice_id", "payment_date", "amount",
            "payment_mode", "reference_number", "notes", "created_at",
            "invoice_number", "client_name"]
    return [dict(zip(cols, r)) for r in rows]


# ---------------------------------------------------------------------------
# Profit & Loss Analytics
# ---------------------------------------------------------------------------
def get_profit_loss_summary(conn, workspace_id: str) -> Dict[str, Any]:
    """Calculate consolidated revenue, expenses, payroll, and real operating profit."""
    ensure_business_ops_schema(conn)
    
    # 1. Invoiced revenue
    inv_row = conn.execute(
        """
        SELECT COALESCE(SUM(total_amount), 0),
               COALESCE(SUM(amount_paid), 0),
               COUNT(id)
        FROM business_invoices
        WHERE workspace_id = ? AND status != 'cancelled'
        """,
        (workspace_id,),
    ).fetchone()
    total_invoiced = float(inv_row[0]) if inv_row else 0.0
    total_collected = float(inv_row[1]) if inv_row else 0.0
    invoice_count = int(inv_row[2]) if inv_row else 0
    outstanding_receivables = round(total_invoiced - total_collected, 2)

    # 2. Approved Expenses
    exp_row = conn.execute(
        """
        SELECT COALESCE(SUM(amount), 0), COUNT(id)
        FROM expense_claims
        WHERE workspace_id = ? AND status IN ('approved', 'settled')
        """,
        (workspace_id,),
    ).fetchone()
    total_expenses = float(exp_row[0]) if exp_row else 0.0
    expense_count = int(exp_row[1]) if exp_row else 0

    # 3. Approved Payroll
    pay_row = conn.execute(
        """
        SELECT COALESCE(SUM(total_gross), 0), COUNT(id)
        FROM payroll_runs
        WHERE workspace_id = ? AND status = 'approved'
        """,
        (workspace_id,),
    ).fetchone()
    total_payroll = float(pay_row[0]) if pay_row else 0.0
    payroll_runs_count = int(pay_row[1]) if pay_row else 0

    # 4. Total Outflows
    total_outflows = round(total_expenses + total_payroll, 2)

    # 5. Operating Profit (Cash basis: Collected - Outflows)
    cash_operating_profit = round(total_collected - total_outflows, 2)

    # 6. Accrual Profit (Accrual basis: Invoiced - Outflows)
    accrual_operating_profit = round(total_invoiced - total_outflows, 2)

    # 7. Pipeline Value (active estimates, quotations, work orders)
    wo_row = conn.execute(
        "SELECT COALESCE(SUM(total_contract_value), 0) FROM business_work_orders WHERE workspace_id = ? AND status != 'closed'",
        (workspace_id,),
    ).fetchone()
    active_contract_value = float(wo_row[0]) if wo_row else 0.0

    quot_row = conn.execute(
        "SELECT COALESCE(SUM(total_amount), 0) FROM business_quotations WHERE workspace_id = ? AND status IN ('sent', 'draft')",
        (workspace_id,),
    ).fetchone()
    pipeline_quotations = float(quot_row[0]) if quot_row else 0.0

    return {
        "workspace_id": workspace_id,
        "total_invoiced_inr": total_invoiced,
        "total_collected_inr": total_collected,
        "outstanding_receivables_inr": outstanding_receivables,
        "total_expenses_inr": total_expenses,
        "total_payroll_inr": total_payroll,
        "total_outflows_inr": total_outflows,
        "cash_operating_profit_inr": cash_operating_profit,
        "accrual_operating_profit_inr": accrual_operating_profit,
        "active_contract_value_inr": active_contract_value,
        "pipeline_quotations_inr": pipeline_quotations,
        "metrics": {
            "invoice_count": invoice_count,
            "expense_count": expense_count,
            "payroll_runs_count": payroll_runs_count,
            "profit_margin_pct": round((accrual_operating_profit / total_invoiced * 100), 1) if total_invoiced > 0 else 0.0,
        },
    }
