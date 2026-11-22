# foundation/domains/lifecycle_enhancements.py
"""
SHAH GROUP AI OS — Lifecycle Enhancements Domain Module
Implements:
1. Dynamic Quotation System (unlimited items, discount, GST, live totals, editing)
2. Complete Survey Site Lifecycle (16 statuses, travel, team, equipment, reminders, payment tracking)
3. GST Invoice & Non-GST Bill System (separate numbering, no GST on Non-GST bills)
4. Registered Vendor Registration & Workflow (profiles, status, approvals)
5. Employee Employment Status & Exit Management (Active, Notice, Exited, clearance)
6. Automated Report Archive & Visual Analytics (real DB analytics, in-app viewer, charts)
"""

import json
import sqlite3
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional, Tuple


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _today() -> str:
    return date.today().isoformat()


def _num_to_words(number: float) -> str:
    """Converts a number to Indian currency words format."""
    try:
        amt = int(round(number))
        if amt == 0:
            return "Zero Rupees Only"
        
        ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
                "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
                "Seventeen", "Eighteen", "Nineteen"]
        tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
        
        def two_digits(n):
            if n < 20:
                return ones[n]
            return tens[n // 10] + (" " + ones[n % 10] if n % 10 != 0 else "")
            
        def three_digits(n):
            if n == 0:
                return ""
            h = n // 100
            rem = n % 100
            res = (ones[h] + " Hundred " if h > 0 else "")
            if rem > 0:
                res += ("and " if h > 0 else "") + two_digits(rem)
            return res.strip()

        crores = amt // 10000000
        rem = amt % 10000000
        lakhs = rem // 100000
        rem = rem % 100000
        thousands = rem // 1000
        rem = rem % 1000
        hundreds = rem

        parts = []
        if crores > 0:
            parts.append(two_digits(crores) + " Crore")
        if lakhs > 0:
            parts.append(two_digits(lakhs) + " Lakh")
        if thousands > 0:
            parts.append(two_digits(thousands) + " Thousand")
        if hundreds > 0:
            parts.append(three_digits(hundreds))
            
        return "Rupees " + " ".join(parts) + " Only"
    except Exception:
        return f"INR {number:,.2f}"


# ==============================================================================
# 1. DYNAMIC QUOTATION SYSTEM
# ==============================================================================

def generate_quotation_number(conn: sqlite3.Connection, workspace_id: str) -> str:
    year = datetime.now().year
    prefix = f"QT-{workspace_id[:3].upper()}-{year}-"
    row = conn.execute(
        "SELECT quotation_number FROM business_quotations WHERE quotation_number LIKE ? ORDER BY id DESC LIMIT 1",
        (f"{prefix}%",)
    ).fetchone()
    if row and row[0]:
        try:
            last_seq = int(row[0].split("-")[-1])
            return f"{prefix}{last_seq + 1:04d}"
        except Exception:
            pass
    return f"{prefix}0001"


def create_dynamic_quotation(conn: sqlite3.Connection, workspace_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a quotation supporting unlimited dynamic item rows, discounts, and item-level GST."""
    items = data.get("items", [])
    if isinstance(items, str):
        try:
            items = json.loads(items)
        except Exception:
            items = []

    clean_items = []
    subtotal = 0.0
    discount_total = 0.0
    computed_gst = 0.0
    default_gst_rate = float(data.get("gst_rate", 18.0))

    for idx, it in enumerate(items, 1):
        desc = it.get("description") or it.get("item_name") or f"Item {idx}"
        unit = it.get("unit", "Nos")
        qty = max(0.0, float(it.get("quantity", 1) or 0.0))
        rate = max(0.0, float(it.get("rate", 0) or 0.0))
        disc = max(0.0, float(it.get("discount", 0) or 0.0))
        item_gst_rate = float(it.get("gst_rate", default_gst_rate) or default_gst_rate)
        
        # Calculate row total
        line_base = qty * rate
        line_taxable = max(0.0, line_base - disc)
        line_gst = round(line_taxable * (item_gst_rate / 100.0), 2)
        line_amount = line_taxable + line_gst

        clean_items.append({
            "item_name": it.get("item_name") or desc,
            "description": desc,
            "unit": unit,
            "quantity": qty,
            "rate": rate,
            "discount": disc,
            "gst_rate": item_gst_rate,
            "taxable_amount": round(line_taxable, 2),
            "gst_amount": line_gst,
            "amount": round(line_amount, 2)
        })

        subtotal += line_base
        discount_total += disc
        computed_gst += line_gst

    taxable_amount = max(0.0, subtotal - discount_total)
    total_amount = round(taxable_amount + computed_gst, 2)
    q_num = data.get("quotation_number") or generate_quotation_number(conn, workspace_id)
    amount_words = _num_to_words(total_amount)

    cur = conn.execute("""
        INSERT INTO business_quotations (
            workspace_id, quotation_number, client_id, estimate_id, project_name,
            subtotal, gst_rate, gst_amount, total_amount, items_json, validity_days,
            terms, status, created_at, discount_total, taxable_amount, client_name,
            client_address, client_contact, amount_in_words
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        workspace_id,
        q_num,
        data.get("client_id") or 0,
        data.get("estimate_id") or 0,
        data.get("project_name", "Survey Proposal"),
        round(subtotal, 2),
        default_gst_rate,
        round(computed_gst, 2),
        total_amount,
        json.dumps(clean_items),
        int(data.get("validity_days", 30)),
        data.get("terms", "Standard 30 days validity. 50% advance with work order."),
        data.get("status", "Draft"),
        _now(),
        round(discount_total, 2),
        round(taxable_amount, 2),
        data.get("client_name", "Valued Client"),
        data.get("client_address", ""),
        data.get("client_contact", ""),
        amount_words
    ))
    conn.commit()
    qid = cur.lastrowid
    return get_dynamic_quotation(conn, qid)


def update_dynamic_quotation(conn: sqlite3.Connection, quotation_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Updates an existing quotation with edited items and terms."""
    items = data.get("items", [])
    if isinstance(items, str):
        try:
            items = json.loads(items)
        except Exception:
            items = []

    clean_items = []
    subtotal = 0.0
    discount_total = 0.0
    computed_gst = 0.0
    default_gst_rate = float(data.get("gst_rate", 18.0))

    for idx, it in enumerate(items, 1):
        desc = it.get("description") or it.get("item_name") or f"Item {idx}"
        unit = it.get("unit", "Nos")
        qty = max(0.0, float(it.get("quantity", 1) or 0.0))
        rate = max(0.0, float(it.get("rate", 0) or 0.0))
        disc = max(0.0, float(it.get("discount", 0) or 0.0))
        item_gst_rate = float(it.get("gst_rate", default_gst_rate) or default_gst_rate)

        line_base = qty * rate
        line_taxable = max(0.0, line_base - disc)
        line_gst = round(line_taxable * (item_gst_rate / 100.0), 2)
        line_amount = line_taxable + line_gst

        clean_items.append({
            "item_name": it.get("item_name") or desc,
            "description": desc,
            "unit": unit,
            "quantity": qty,
            "rate": rate,
            "discount": disc,
            "gst_rate": item_gst_rate,
            "taxable_amount": round(line_taxable, 2),
            "gst_amount": line_gst,
            "amount": round(line_amount, 2)
        })

        subtotal += line_base
        discount_total += disc
        computed_gst += line_gst

    taxable_amount = max(0.0, subtotal - discount_total)
    total_amount = round(taxable_amount + computed_gst, 2)
    amount_words = _num_to_words(total_amount)

    conn.execute("""
        UPDATE business_quotations
        SET project_name = ?, client_name = ?, client_address = ?, client_contact = ?,
            subtotal = ?, gst_rate = ?, gst_amount = ?, total_amount = ?,
            discount_total = ?, taxable_amount = ?, items_json = ?, validity_days = ?,
            terms = ?, status = ?, amount_in_words = ?
        WHERE id = ?
    """, (
        data.get("project_name", "Survey Proposal"),
        data.get("client_name", ""),
        data.get("client_address", ""),
        data.get("client_contact", ""),
        round(subtotal, 2),
        default_gst_rate,
        round(computed_gst, 2),
        total_amount,
        round(discount_total, 2),
        round(taxable_amount, 2),
        json.dumps(clean_items),
        int(data.get("validity_days", 30)),
        data.get("terms", ""),
        data.get("status", "Sent"),
        amount_words,
        quotation_id
    ))
    conn.commit()
    return get_dynamic_quotation(conn, quotation_id)


def get_dynamic_quotation(conn: sqlite3.Connection, quotation_id: int) -> Optional[Dict[str, Any]]:
    cur = conn.execute("SELECT * FROM business_quotations WHERE id = ?", (quotation_id,))
    row = cur.fetchone()
    if not row:
        return None
    cols = [c[0] for c in cur.description]
    d = dict(zip(cols, row))
    try:
        d["items"] = json.loads(d.get("items_json") or "[]")
    except Exception:
        d["items"] = []
    return d


# ==============================================================================
# 2. SURVEY SITE LIFECYCLE & FINANCIAL TRACKING
# ==============================================================================

VALID_SURVEY_STATUSES = [
    "Site Scheduled",
    "Team Assigned",
    "Travel Planned",
    "Survey Pending",
    "Survey In Progress",
    "Field Survey Completed",
    "Data Processing",
    "Report Preparation",
    "Report Under Review",
    "Report Completed",
    "Report Submitted",
    "Client Approval Pending",
    "Payment Pending",
    "Partially Paid",
    "Payment Received",
    "Closed"
]

COMPLETED_SURVEY_STATUSES = [
    "Field Survey Completed",
    "Data Processing",
    "Report Preparation",
    "Report Under Review",
    "Report Completed",
    "Report Submitted",
    "Client Approval Pending",
    "Payment Pending",
    "Partially Paid",
    "Payment Received",
    "Closed"
]

def generate_site_code(conn: sqlite3.Connection, workspace_id: str) -> str:
    prefix = f"SITE-{workspace_id[:3].upper()}-"
    row = conn.execute(
        "SELECT code FROM sites WHERE code LIKE ? ORDER BY id DESC LIMIT 1",
        (f"{prefix}%",)
    ).fetchone()
    if row and row[0]:
        try:
            last_seq = int(row[0].split("-")[-1])
            return f"{prefix}{last_seq + 1:03d}"
        except Exception:
            pass
    return f"{prefix}001"


def create_lifecycle_site(conn: sqlite3.Connection, workspace_id: str, data: Dict[str, Any], user_name: str = "Admin") -> Dict[str, Any]:
    code = data.get("code")
    if not code:
        code = generate_site_code(conn, workspace_id)
    else:
        # Ensure code is unique
        existing = conn.execute("SELECT id FROM sites WHERE code = ?", (code,)).fetchone()
        if existing:
            code = f"{code}-{int(datetime.now().timestamp()) % 10000:04d}"

    name = data.get("name", "Untitled Survey Project")
    status = data.get("survey_status") or "Site Scheduled"
    if status not in VALID_SURVEY_STATUSES:
        status = "Site Scheduled"

    initial_history = [{
        "status": status,
        "changed_by": user_name,
        "timestamp": _now(),
        "remarks": data.get("special_instructions") or "Site created and scheduled"
    }]

    project_val = float(data.get("project_value", 0.0) or 0.0)
    advance_val = float(data.get("advance_received", 0.0) or 0.0)
    balance_due = max(0.0, project_val - advance_val)

    payment_status = "Not Invoiced"
    if advance_val > 0 and balance_due > 0:
        payment_status = "Partially Paid"
    elif advance_val >= project_val and project_val > 0:
        payment_status = "Fully Paid"

    cur = conn.execute("""
        INSERT INTO sites (
            workspace_id, name, code, address, geofence_radius_m, field_policy_required,
            created_at, status, client_name, project_location, complete_address,
            coordinates, survey_type, scope_of_work, start_date, expected_completion_date,
            assigned_team, team_leader, equipment_assigned, transport_details,
            estimated_expenses, special_instructions, required_documents, site_contact_person,
            site_contact_phone, survey_status, status_history, project_value, advance_received,
            invoice_generated, total_billed, payment_received, balance_due, payment_due_date,
            last_followup_date, next_followup_date, payment_status, documents_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        workspace_id,
        name,
        code,
        data.get("complete_address") or data.get("address", ""),
        float(data.get("geofence_radius_m", 150.0)),
        int(data.get("field_policy_required", 1)),
        _now(),
        "active",
        data.get("client_name", ""),
        data.get("project_location", ""),
        data.get("complete_address", ""),
        data.get("coordinates", ""),
        data.get("survey_type", "Topographic Survey"),
        data.get("scope_of_work", ""),
        data.get("start_date", _today()),
        data.get("expected_completion_date", ""),
        json.dumps(data.get("assigned_team") or []),
        data.get("team_leader", ""),
        json.dumps(data.get("equipment_assigned") or []),
        data.get("transport_details", ""),
        float(data.get("estimated_expenses", 0.0) or 0.0),
        data.get("special_instructions", ""),
        data.get("required_documents", ""),
        data.get("site_contact_person", ""),
        data.get("site_contact_phone", ""),
        status,
        json.dumps(initial_history),
        project_val,
        advance_val,
        data.get("invoice_generated", ""),
        float(data.get("total_billed", project_val) or project_val),
        advance_val,
        balance_due,
        data.get("payment_due_date", ""),
        data.get("last_followup_date", ""),
        data.get("next_followup_date", ""),
        payment_status,
        json.dumps(data.get("documents_json") or [])
    ))
    conn.commit()
    sid = cur.lastrowid
    return get_site_details(conn, sid)


def update_site_status(conn: sqlite3.Connection, site_id: int, new_status: str, remarks: str = "", user_name: str = "Admin") -> Optional[Dict[str, Any]]:
    """Updates a site's survey status and appends to the audit history."""
    if new_status not in VALID_SURVEY_STATUSES:
        raise ValueError(f"Invalid status: {new_status}. Must be one of {VALID_SURVEY_STATUSES}")

    row = conn.execute("SELECT status_history FROM sites WHERE id = ?", (site_id,)).fetchone()
    if not row:
        return None

    try:
        history = json.loads(row[0] or "[]")
    except Exception:
        history = []

    history.append({
        "status": new_status,
        "changed_by": user_name,
        "timestamp": _now(),
        "remarks": remarks
    })

    conn.execute("""
        UPDATE sites
        SET survey_status = ?, status_history = ?
        WHERE id = ?
    """, (new_status, json.dumps(history), site_id))
    conn.commit()
    return get_site_details(conn, site_id)


def update_site_payment(conn: sqlite3.Connection, site_id: int, data: Dict[str, Any], user_name: str = "Admin") -> Optional[Dict[str, Any]]:
    """Updates independent financial tracking on a site."""
    site = get_site_details(conn, site_id)
    if not site:
        return None

    project_val = float(data.get("project_value", site.get("project_value", 0.0)))
    advance_val = float(data.get("advance_received", site.get("advance_received", 0.0)))
    payment_rec = float(data.get("payment_received", site.get("payment_received", 0.0)))
    total_billed = float(data.get("total_billed", site.get("total_billed", project_val)))

    total_paid = advance_val + payment_rec
    balance_due = max(0.0, total_billed - total_paid)

    # Determine payment status
    if total_billed == 0:
        pay_status = "Not Invoiced"
    elif total_paid >= total_billed and total_billed > 0:
        pay_status = "Fully Paid"
    elif total_paid > 0 and balance_due > 0:
        pay_status = "Partially Paid"
    else:
        pay_status = "Payment Pending"

    due_date = data.get("payment_due_date") or site.get("payment_due_date", "")
    if due_date and due_date < _today() and balance_due > 0:
        pay_status = "Overdue Payment"

    conn.execute("""
        UPDATE sites
        SET project_value = ?, advance_received = ?, total_billed = ?, payment_received = ?,
            balance_due = ?, payment_status = ?, invoice_generated = ?, payment_due_date = ?,
            last_followup_date = ?, next_followup_date = ?
        WHERE id = ?
    """, (
        project_val,
        advance_val,
        total_billed,
        payment_rec,
        balance_due,
        pay_status,
        data.get("invoice_generated") or site.get("invoice_generated", ""),
        due_date,
        data.get("last_followup_date") or site.get("last_followup_date", ""),
        data.get("next_followup_date") or site.get("next_followup_date", ""),
        site_id
    ))
    conn.commit()
    return get_site_details(conn, site_id)


def get_site_details(conn: sqlite3.Connection, site_id: int) -> Optional[Dict[str, Any]]:
    cur = conn.execute("SELECT * FROM sites WHERE id = ?", (site_id,))
    row = cur.fetchone()
    if not row:
        return None
    cols = [c[0] for c in cur.description]
    d = dict(zip(cols, row))
    for json_field in ["assigned_team", "equipment_assigned", "status_history", "documents_json"]:
        try:
            d[json_field] = json.loads(d.get(json_field) or "[]")
        except Exception:
            d[json_field] = []

    # Calculate schedule categorization
    today_str = _today()
    tomorrow_str = (date.today() + timedelta(days=1)).isoformat()
    s_date = d.get("start_date") or ""

    if s_date == today_str:
        d["schedule_category"] = "Today's Site Visit"
    elif s_date == tomorrow_str:
        d["schedule_category"] = "Tomorrow's Site"
    elif s_date > tomorrow_str:
        d["schedule_category"] = "Upcoming Site"
    elif s_date < today_str and d.get("survey_status") in ["Site Scheduled", "Team Assigned", "Travel Planned", "Survey Pending"]:
        d["schedule_category"] = "Overdue Site Visit"
    elif d.get("survey_status") in COMPLETED_SURVEY_STATUSES:
        d["schedule_category"] = "Completed Site"
    else:
        d["schedule_category"] = "Active Site"

    return d


def list_lifecycle_sites(conn: sqlite3.Connection, workspace_id: Optional[str] = None, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    sql = "SELECT id FROM sites"
    params = []
    if workspace_id and workspace_id != "ALL":
        sql += " WHERE workspace_id = ?"
        params.append(workspace_id)
    sql += " ORDER BY id DESC"

    rows = conn.execute(sql, params).fetchall()
    all_sites = [get_site_details(conn, r[0]) for r in rows if r[0]]

    if not category_filter or category_filter == "all":
        return all_sites

    cat = category_filter.lower()
    filtered = []
    for s in all_sites:
        scat = s.get("schedule_category", "").lower()
        pstat = s.get("payment_status", "").lower()
        bal = float(s.get("balance_due", 0.0))

        if cat == "upcoming" and "upcoming" in scat:
            filtered.append(s)
        elif cat == "tomorrow" and "tomorrow" in scat:
            filtered.append(s)
        elif cat == "today" and "today" in scat:
            filtered.append(s)
        elif cat == "overdue" and "overdue" in scat:
            filtered.append(s)
        elif cat == "completed" and "completed" in scat:
            filtered.append(s)
        elif cat == "payment_pending" and bal > 0 and s.get("survey_status") in COMPLETED_SURVEY_STATUSES:
            filtered.append(s)
        elif cat == "overdue_payment" and ("overdue" in pstat or (s.get("payment_due_date") and s.get("payment_due_date") < _today() and bal > 0)):
            filtered.append(s)
        elif cat == "partially_paid" and "partial" in pstat:
            filtered.append(s)
        elif cat == "payments_received" and ("fully" in pstat or (bal == 0 and float(s.get("project_value", 0)) > 0)):
            filtered.append(s)

    return filtered


# ==============================================================================
# 3. GST INVOICE VS NON-GST BILL SYSTEM
# ==============================================================================

def generate_bill_number(conn: sqlite3.Connection, workspace_id: str, bill_type: str = "NON_GST") -> str:
    year = datetime.now().year
    prefix = f"BILL-{workspace_id[:3].upper()}-{year}-" if bill_type == "NON_GST" else f"INV-{workspace_id[:3].upper()}-{year}-"
    row = conn.execute(
        "SELECT invoice_number FROM business_invoices WHERE invoice_number LIKE ? ORDER BY id DESC LIMIT 1",
        (f"{prefix}%",)
    ).fetchone()
    if row and row[0]:
        try:
            last_seq = int(row[0].split("-")[-1])
            return f"{prefix}{last_seq + 1:04d}"
        except Exception:
            pass
    return f"{prefix}0001"


def create_billing_document(conn: sqlite3.Connection, workspace_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a GST Tax Invoice or a compliant Non-GST Commercial Bill."""
    bill_type = data.get("bill_type", "GST").upper()
    if bill_type not in ["GST", "NON_GST"]:
        bill_type = "GST"

    doc_num = data.get("bill_number") or data.get("invoice_number") or generate_bill_number(conn, workspace_id, bill_type)
    items = data.get("items", [])
    if isinstance(items, str):
        try:
            items = json.loads(items)
        except Exception:
            items = []

    subtotal = 0.0
    clean_items = []
    discount_amount = max(0.0, float(data.get("discount_amount", 0.0) or 0.0))

    for idx, it in enumerate(items, 1):
        desc = it.get("item") or it.get("description") or f"Service {idx}"
        unit = it.get("unit", "Nos")
        qty = max(0.0, float(it.get("quantity", 1) or 0.0))
        rate = max(0.0, float(it.get("rate", 0) or 0.0))
        line_amt = qty * rate

        clean_items.append({
            "item": desc,
            "description": desc,
            "unit": unit,
            "quantity": qty,
            "rate": rate,
            "amount": round(line_amt, 2)
        })
        subtotal += line_amt

    taxable = max(0.0, subtotal - discount_amount)

    if bill_type == "NON_GST":
        # Strictly zero tax for Non-GST
        cgst = 0.0
        sgst = 0.0
        igst = 0.0
        total_tax = 0.0
        total_amount = round(taxable, 2)
    else:
        # Full GST calculation
        is_interstate = bool(data.get("is_interstate", False))
        gst_rate = float(data.get("gst_rate", 18.0) or 18.0)
        total_tax = round(taxable * (gst_rate / 100.0), 2)
        if is_interstate:
            cgst = 0.0
            sgst = 0.0
            igst = total_tax
        else:
            cgst = round(total_tax / 2.0, 2)
            sgst = round(total_tax - cgst, 2)
            igst = 0.0
        total_amount = round(taxable + total_tax, 2)

    amount_words = _num_to_words(total_amount)

    cur = conn.execute("""
        INSERT INTO business_invoices (
            workspace_id, invoice_number, work_order_id, client_id, invoice_date,
            due_date, subtotal, cgst_amount, sgst_amount, igst_amount, total_tax,
            total_amount, items_json, amount_paid, payment_status, status, created_at,
            bill_type, bill_number, client_name, client_address, client_contact,
            description_of_work, discount_amount, amount_in_words, payment_mode,
            notes, authorized_signature
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        workspace_id,
        doc_num,
        data.get("work_order_id") or 0,
        data.get("client_id") or 0,
        data.get("invoice_date") or _today(),
        data.get("due_date") or (date.today() + timedelta(days=15)).isoformat(),
        round(subtotal, 2),
        cgst,
        sgst,
        igst,
        total_tax,
        total_amount,
        json.dumps(clean_items),
        0.0,
        "Pending",
        "Issued",
        _now(),
        bill_type,
        doc_num,
        data.get("client_name", "Valued Client"),
        data.get("client_address", ""),
        data.get("client_contact", ""),
        data.get("description_of_work", "Professional Services Rendered"),
        discount_amount,
        amount_words,
        data.get("payment_mode", "NEFT / RTGS"),
        data.get("notes", "Payment due within 15 days of presentation."),
        data.get("authorized_signature", "For SHAH GROUP")
    ))
    conn.commit()
    inv_id = cur.lastrowid
    return get_billing_document(conn, inv_id)


def get_billing_document(conn: sqlite3.Connection, doc_id: int) -> Optional[Dict[str, Any]]:
    cur = conn.execute("SELECT * FROM business_invoices WHERE id = ?", (doc_id,))
    row = cur.fetchone()
    if not row:
        return None
    cols = [c[0] for c in cur.description]
    d = dict(zip(cols, row))
    try:
        d["items"] = json.loads(d.get("items_json") or "[]")
    except Exception:
        d["items"] = []
    return d


def list_billing_documents(conn: sqlite3.Connection, workspace_id: Optional[str] = None, bill_type: Optional[str] = None) -> List[Dict[str, Any]]:
    sql = "SELECT id FROM business_invoices WHERE 1=1"
    params = []
    if workspace_id and workspace_id != "ALL":
        sql += " AND workspace_id = ?"
        params.append(workspace_id)
    if bill_type and bill_type.upper() not in ("ALL", "*"):
        sql += " AND bill_type = ?"
        params.append(bill_type.upper())
    sql += " ORDER BY id DESC"

    rows = conn.execute(sql, params).fetchall()
    return [get_billing_document(conn, r[0]) for r in rows if r[0]]


# ==============================================================================
# 4. REGISTERED VENDOR MANAGEMENT
# ==============================================================================

VALID_VENDOR_STATUSES = [
    "Draft",
    "Registration Pending",
    "Documents Pending",
    "Under Verification",
    "Approved",
    "Active",
    "Inactive",
    "Rejected"
]

def register_vendor(conn: sqlite3.Connection, workspace_id: str, data: Dict[str, Any], user_name: str = "Admin") -> Dict[str, Any]:
    name = data.get("company_name") or data.get("name") or "New Vendor"
    status = data.get("status") or "Approved"
    if status not in VALID_VENDOR_STATUSES:
        status = "Approved"

    initial_history = [{
        "status": status,
        "changed_by": user_name,
        "timestamp": _now(),
        "remarks": "Vendor initial registration"
    }]

    cur = conn.execute("""
        INSERT INTO expense_vendors (
            workspace_id, name, category, contact, created_at, company_name,
            contact_person, mobile, email, address, city, state, pincode,
            gstin, pan, msme_udyam, bank_name, bank_account, bank_ifsc,
            bank_branch, services_supplied, registration_date, documents_json,
            status, notes, status_history
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        workspace_id,
        name,
        data.get("category", "General Supplies"),
        data.get("mobile") or data.get("contact", ""),
        _now(),
        name,
        data.get("contact_person", ""),
        data.get("mobile", ""),
        data.get("email", ""),
        data.get("address", ""),
        data.get("city", ""),
        data.get("state", ""),
        data.get("pincode", ""),
        data.get("gstin", ""),
        data.get("pan", ""),
        data.get("msme_udyam", ""),
        data.get("bank_name", ""),
        data.get("bank_account", ""),
        data.get("bank_ifsc", ""),
        data.get("bank_branch", ""),
        data.get("services_supplied", ""),
        data.get("registration_date") or _today(),
        json.dumps(data.get("documents_json") or []),
        status,
        data.get("notes", ""),
        json.dumps(initial_history)
    ))
    conn.commit()
    vid = cur.lastrowid
    return get_vendor_details(conn, vid)


def update_vendor(conn: sqlite3.Connection, vendor_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    name = data.get("company_name") or data.get("name")
    conn.execute("""
        UPDATE expense_vendors
        SET name = COALESCE(?, name),
            company_name = COALESCE(?, company_name),
            category = COALESCE(?, category),
            contact_person = COALESCE(?, contact_person),
            mobile = COALESCE(?, mobile),
            contact = COALESCE(?, contact),
            email = COALESCE(?, email),
            address = COALESCE(?, address),
            city = COALESCE(?, city),
            state = COALESCE(?, state),
            pincode = COALESCE(?, pincode),
            gstin = COALESCE(?, gstin),
            pan = COALESCE(?, pan),
            msme_udyam = COALESCE(?, msme_udyam),
            bank_name = COALESCE(?, bank_name),
            bank_account = COALESCE(?, bank_account),
            bank_ifsc = COALESCE(?, bank_ifsc),
            bank_branch = COALESCE(?, bank_branch),
            services_supplied = COALESCE(?, services_supplied),
            notes = COALESCE(?, notes)
        WHERE id = ?
    """, (
        name, name, data.get("category"), data.get("contact_person"),
        data.get("mobile"), data.get("mobile"), data.get("email"),
        data.get("address"), data.get("city"), data.get("state"), data.get("pincode"),
        data.get("gstin"), data.get("pan"), data.get("msme_udyam"),
        data.get("bank_name"), data.get("bank_account"), data.get("bank_ifsc"), data.get("bank_branch"),
        data.get("services_supplied"), data.get("notes"),
        vendor_id
    ))
    conn.commit()
    return get_vendor_details(conn, vendor_id)


def update_vendor_status(conn: sqlite3.Connection, vendor_id: int, new_status: str, remarks: str = "", user_name: str = "Admin") -> Optional[Dict[str, Any]]:
    if new_status not in VALID_VENDOR_STATUSES:
        raise ValueError(f"Invalid vendor status: {new_status}")

    row = conn.execute("SELECT status_history FROM expense_vendors WHERE id = ?", (vendor_id,)).fetchone()
    if not row:
        return None

    try:
        history = json.loads(row[0] or "[]")
    except Exception:
        history = []

    history.append({
        "status": new_status,
        "changed_by": user_name,
        "timestamp": _now(),
        "remarks": remarks
    })

    conn.execute("""
        UPDATE expense_vendors
        SET status = ?, status_history = ?
        WHERE id = ?
    """, (new_status, json.dumps(history), vendor_id))
    conn.commit()
    return get_vendor_details(conn, vendor_id)


def get_vendor_details(conn: sqlite3.Connection, vendor_id: int) -> Optional[Dict[str, Any]]:
    cur = conn.execute("SELECT * FROM expense_vendors WHERE id = ?", (vendor_id,))
    row = cur.fetchone()
    if not row:
        return None
    cols = [c[0] for c in cur.description]
    d = dict(zip(cols, row))
    try:
        d["status_history"] = json.loads(d.get("status_history") or "[]")
    except Exception:
        d["status_history"] = []
    try:
        d["documents_json"] = json.loads(d.get("documents_json") or "[]")
    except Exception:
        d["documents_json"] = []
    return d


def list_registered_vendors(conn: sqlite3.Connection, workspace_id: Optional[str] = None, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    sql = "SELECT id FROM expense_vendors WHERE 1=1"
    params = []
    if workspace_id and workspace_id != "ALL":
        sql += " AND workspace_id = ?"
        params.append(workspace_id)
    if status_filter and status_filter.lower() != "all":
        sql += " AND status = ?"
        params.append(status_filter)
    sql += " ORDER BY id DESC"

    rows = conn.execute(sql, params).fetchall()
    return [get_vendor_details(conn, r[0]) for r in rows if r[0]]


# ==============================================================================
# 5. EMPLOYEE EMPLOYMENT STATUS & EXIT MANAGEMENT
# ==============================================================================

VALID_EMPLOYEE_STATUSES = [
    "Active",
    "On Leave",
    "Notice Period",
    "Resigned",
    "Terminated",
    "Exited",
    "Inactive"
]

def update_employee_employment_status(conn: sqlite3.Connection, employee_id: int, data: Dict[str, Any], user_name: str = "Admin") -> Optional[Dict[str, Any]]:
    new_status = data.get("employment_status") or data.get("status")
    if new_status not in VALID_EMPLOYEE_STATUSES:
        raise ValueError(f"Invalid employee status: {new_status}")

    row = conn.execute("SELECT status_history FROM employees WHERE id = ?", (employee_id,)).fetchone()
    if not row:
        return None

    try:
        history = json.loads(row[0] or "[]")
    except Exception:
        history = []

    history.append({
        "status": new_status,
        "changed_by": user_name,
        "timestamp": _now(),
        "remarks": data.get("exit_remarks") or data.get("remarks") or f"Status changed to {new_status}"
    })

    # Base status field for backward compatibility
    base_status = "active" if new_status in ["Active", "On Leave"] else "inactive"

    conn.execute("""
        UPDATE employees
        SET employment_status = ?,
            status = ?,
            exit_date = COALESCE(?, exit_date),
            last_working_date = COALESCE(?, last_working_date),
            reason_for_leaving = COALESCE(?, reason_for_leaving),
            exit_type = COALESCE(?, exit_type),
            notice_period_details = COALESCE(?, notice_period_details),
            handover_status = COALESCE(?, handover_status),
            final_settlement_status = COALESCE(?, final_settlement_status),
            exit_remarks = COALESCE(?, exit_remarks),
            status_history = ?
        WHERE id = ?
    """, (
        new_status,
        base_status,
        data.get("exit_date"),
        data.get("last_working_date"),
        data.get("reason_for_leaving"),
        data.get("exit_type"),
        data.get("notice_period_details"),
        data.get("handover_status"),
        data.get("final_settlement_status"),
        data.get("exit_remarks"),
        json.dumps(history),
        employee_id
    ))
    conn.commit()
    return get_employee_lifecycle_details(conn, employee_id)


def get_employee_lifecycle_details(conn: sqlite3.Connection, employee_id: int) -> Optional[Dict[str, Any]]:
    cur = conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
    row = cur.fetchone()
    if not row:
        return None
    cols = [c[0] for c in cur.description]
    d = dict(zip(cols, row))
    try:
        d["status_history"] = json.loads(d.get("status_history") or "[]")
    except Exception:
        d["status_history"] = []
    return d


def list_employees_filtered(conn: sqlite3.Connection, workspace_id: Optional[str] = None, filter_mode: str = "active") -> List[Dict[str, Any]]:
    """
    filter_mode:
      - 'active': only Active and On Leave (for team assignments and active operations)
      - 'former': Notice Period, Resigned, Terminated, Exited, Inactive
      - 'all': entire historical staff records
    """
    sql = "SELECT id FROM employees WHERE 1=1"
    params = []
    if workspace_id and workspace_id != "ALL":
        sql += " AND workspace_id = ?"
        params.append(workspace_id)

    mode = filter_mode.lower()
    if mode == "active":
        sql += " AND (employment_status IS NULL OR employment_status IN ('Active', 'On Leave'))"
    elif mode == "former":
        sql += " AND employment_status IN ('Notice Period', 'Resigned', 'Terminated', 'Exited', 'Inactive')"

    sql += " ORDER BY id DESC"
    rows = conn.execute(sql, params).fetchall()
    return [get_employee_lifecycle_details(conn, r[0]) for r in rows if r[0]]


# ==============================================================================
# 6. AUTOMATED REPORT ARCHIVE & VISUAL ANALYTICS
# ==============================================================================

def generate_business_report(conn: sqlite3.Connection, workspace_id: str, report_type: str = "MONTHLY_PERFORMANCE", date_range: str = "Last 30 Days") -> Dict[str, Any]:
    """Generates a complete business report from actual database records and archives it."""
    # 1. Fetch live numbers
    invoices = conn.execute("SELECT total_amount, bill_type, payment_status FROM business_invoices WHERE workspace_id = ?", (workspace_id,)).fetchall()
    total_rev = sum(float(r[0] or 0.0) for r in invoices)
    gst_rev = sum(float(r[0] or 0.0) for r in invoices if (r[1] or "GST").upper() == "GST")
    nongst_rev = sum(float(r[0] or 0.0) for r in invoices if (r[1] or "GST").upper() == "NON_GST")

    sites = conn.execute("SELECT survey_status, balance_due, project_value FROM sites WHERE workspace_id = ?", (workspace_id,)).fetchall()
    total_sites = len(sites)
    completed_sites = sum(1 for s in sites if s[0] in COMPLETED_SURVEY_STATUSES)
    total_receivables = sum(float(s[1] or 0.0) for s in sites)

    quotations = conn.execute("SELECT total_amount, status FROM business_quotations WHERE workspace_id = ?", (workspace_id,)).fetchall()
    total_quotations = len(quotations)
    total_quoted_val = sum(float(q[0] or 0.0) for q in quotations)

    employees = conn.execute("SELECT employment_status FROM employees WHERE workspace_id = ?", (workspace_id,)).fetchall()
    active_emps = sum(1 for e in employees if (e[0] or "Active") in ["Active", "On Leave"])
    former_emps = sum(1 for e in employees if (e[0] or "Active") in ["Resigned", "Terminated", "Exited", "Inactive"])

    # 2. Build structured executive summary
    title = f"{workspace_id} Comprehensive Business & Operations Performance Report"
    period_label = datetime.now().strftime("%B %Y")
    
    exec_summary = (
        f"Executive summary for {workspace_id} covering operational lifecycle and financial settlement. "
        f"Total active sites logged: {total_sites} ({completed_sites} completed). "
        f"Total revenue billed to date: INR {total_rev:,.2f} (GST: INR {gst_rev:,.2f}, Non-GST: INR {nongst_rev:,.2f}). "
        f"Outstanding client balance across active sites: INR {total_receivables:,.2f}. "
        f"Active workforce stands at {active_emps} personnel."
    )

    # 3. Tabular metrics
    detailed_tables = [
        {
            "section_name": "Revenue & Billing Breakdown",
            "headers": ["Metric", "Amount (INR)", "Share / Ratio"],
            "rows": [
                ["Total Billed Value", f"INR {total_rev:,.2f}", "100.0%"],
                ["GST Tax Invoices", f"INR {gst_rev:,.2f}", f"{(gst_rev/total_rev*100) if total_rev else 0:.1f}%"],
                ["Non-GST Commercial Bills", f"INR {nongst_rev:,.2f}", f"{(nongst_rev/total_rev*100) if total_rev else 0:.1f}%"],
                ["Outstanding Site Receivables", f"INR {total_receivables:,.2f}", "Uncollected Balance"]
            ]
        },
        {
            "section_name": "Survey & Project Operations Lifecycle",
            "headers": ["Operational Indicator", "Count / Value", "Operational Status"],
            "rows": [
                ["Total Survey Sites", str(total_sites), "Active Portfolio"],
                ["Field Surveys Completed", str(completed_sites), f"{(completed_sites/total_sites*100) if total_sites else 0:.1f}% Completed"],
                ["Commercial Quotations Issued", str(total_quotations), f"Valued at INR {total_quoted_val:,.2f}"],
                ["Active Field Staff", str(active_emps), f"{former_emps} former staff in archive"]
            ]
        }
    ]

    # 4. Charts data series
    charts = {
        "billing_distribution": {
            "type": "donut",
            "labels": ["GST Invoices", "Non-GST Bills", "Pending Receivables"],
            "values": [gst_rev, nongst_rev, total_receivables]
        },
        "operations_breakdown": {
            "type": "bar",
            "labels": ["Total Sites", "Completed Surveys", "Quotations Issued", "Active Staff"],
            "values": [total_sites, completed_sites, total_quotations, active_emps]
        }
    }

    key_metrics = {
        "total_revenue": total_rev,
        "gst_revenue": gst_rev,
        "nongst_revenue": nongst_rev,
        "total_sites": total_sites,
        "completed_sites": completed_sites,
        "outstanding_receivables": total_receivables,
        "active_employees": active_emps
    }

    pending_actions = []
    if total_receivables > 0:
        pending_actions.append(f"Follow up on outstanding receivables totaling INR {total_receivables:,.2f}.")
    if total_sites > completed_sites:
        pending_actions.append(f"Advance field and data processing workflows on {total_sites - completed_sites} pending site visits.")
    if not pending_actions:
        pending_actions.append("All site operations and payment collections are currently up to date.")

    cur = conn.execute("""
        INSERT INTO business_reports (
            workspace_id, report_type, title, period_label, date_range,
            generated_at, summary, executive_summary, detailed_tables_json,
            charts_json, key_metrics_json, pending_actions_json, status, author_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        workspace_id,
        report_type,
        title,
        period_label,
        date_range,
        _now(),
        exec_summary,
        exec_summary,
        json.dumps(detailed_tables),
        json.dumps(charts),
        json.dumps(key_metrics),
        json.dumps(pending_actions),
        "Completed",
        1
    ))
    conn.commit()
    rid = cur.lastrowid
    return get_report_details(conn, rid)


def get_report_details(conn: sqlite3.Connection, report_id: int) -> Optional[Dict[str, Any]]:
    cur = conn.execute("SELECT * FROM business_reports WHERE id = ?", (report_id,))
    row = cur.fetchone()
    if not row:
        return None
    cols = [c[0] for c in cur.description]
    d = dict(zip(cols, row))
    for j_field in ["detailed_tables_json", "charts_json", "key_metrics_json", "pending_actions_json"]:
        try:
            d[j_field] = json.loads(d.get(j_field) or ("{}" if "charts" in j_field or "key" in j_field else "[]"))
        except Exception:
            d[j_field] = {} if "charts" in j_field or "key" in j_field else []
    return d


def list_archived_reports(conn: sqlite3.Connection, workspace_id: Optional[str] = None) -> List[Dict[str, Any]]:
    sql = "SELECT id FROM business_reports WHERE 1=1"
    params = []
    if workspace_id and workspace_id != "ALL":
        sql += " AND workspace_id = ?"
        params.append(workspace_id)
    sql += " ORDER BY id DESC"

    rows = conn.execute(sql, params).fetchall()
    return [get_report_details(conn, r[0]) for r in rows if r[0]]


def get_reports_analytics_summary(conn: sqlite3.Connection, workspace_id: Optional[str] = None) -> Dict[str, Any]:
    """Generates top-level analytics dashboard summary computed directly from live DB."""
    ws = workspace_id if (workspace_id and workspace_id != "ALL") else "SSC"

    # Invoices
    inv_rows = conn.execute("SELECT total_amount, bill_type, payment_status FROM business_invoices WHERE workspace_id = ?", (ws,)).fetchall()
    total_rev = sum(float(r[0] or 0.0) for r in inv_rows)
    gst_rev = sum(float(r[0] or 0.0) for r in inv_rows if (r[1] or "GST").upper() == "GST")
    nongst_rev = sum(float(r[0] or 0.0) for r in inv_rows if (r[1] or "GST").upper() == "NON_GST")

    # Sites
    site_rows = conn.execute("SELECT survey_status, balance_due, project_value FROM sites WHERE workspace_id = ?", (ws,)).fetchall()
    total_sites = len(site_rows)
    completed_sites = sum(1 for s in site_rows if s[0] in COMPLETED_SURVEY_STATUSES)
    receivables = sum(float(s[1] or 0.0) for s in site_rows)

    # Quotations
    q_rows = conn.execute("SELECT total_amount, status FROM business_quotations WHERE workspace_id = ?", (ws,)).fetchall()
    quot_count = len(q_rows)
    quot_val = sum(float(q[0] or 0.0) for q in q_rows)

    # Reports
    rep_rows = conn.execute("SELECT status, generated_at FROM business_reports WHERE workspace_id = ? ORDER BY id DESC", (ws,)).fetchall()
    total_reports = len(rep_rows)
    last_rep_date = rep_rows[0][1] if rep_rows else "Never"

    return {
        "total_reports": total_reports,
        "reports_generated": total_reports,
        "pending_reports": 0,
        "failed_reports": 0,
        "last_generated_report": last_rep_date,
        "analytics": {
            "total_revenue": total_rev,
            "gst_revenue": gst_rev,
            "nongst_revenue": nongst_rev,
            "total_sites": total_sites,
            "completed_sites": completed_sites,
            "outstanding_receivables": receivables,
            "quotation_count": quot_count,
            "quotation_total_value": quot_val
        }
    }
