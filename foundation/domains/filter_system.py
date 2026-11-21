# -*- coding: utf-8 -*-
"""SHAH GROUP AI OS — Universal Filter & Export System.

Features:
  1. Real backend SQL-powered filtering engine across all core operational tables:
     - tasks (employee_tasks)
     - sites (sites / projects)
     - estimates (business_estimates)
     - quotations (business_quotations)
     - work_orders (business_work_orders)
     - invoices (business_invoices)
     - expenses (expense_claims)
     - leads (social_leads)
     - media (social_media_assets)
     - studio (studio_projects)
     - clients (social_client_profiles)
  2. Multi-criteria query combining:
     - Full-text search (LIKE %query%)
     - Date range (from_date to to_date)
     - Status, Priority, Category
     - Assigned Employee / Client / Project
     - Workspace isolation (SSC, INFRA, OTHER, or ALL)
  3. Dynamic sorting and pagination (page, limit, total_count, total_pages).
  4. Real CSV and JSON export generation with sanitized headers and escaping.
  5. Active filter summary indicators for UI state hydration.
"""
from __future__ import annotations

import csv
import io
import re
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ..store import Store

KOLKATA_TZ = timezone(timedelta(hours=5, minutes=30))

# Searchable columns mapping per operational table
TABLE_CONFIG: Dict[str, Dict[str, Any]] = {
    "tasks": {
        "table": "employee_tasks",
        "search_cols": ["title", "description", "category", "project_id"],
        "date_col": "deadline_date",
        "workspace_col": "workspace_id",
        "status_col": "status",
        "priority_col": "priority",
        "category_col": "category",
        "emp_col": "assigned_to"
    },
    "sites": {
        "table": "sites",
        "search_cols": ["code", "name", "address"],
        "date_col": "created_at",
        "workspace_col": "workspace_id",
        "status_col": "status",
        "priority_col": None,
        "category_col": None,
        "emp_col": None
    },
    "estimates": {
        "table": "business_estimates",
        "search_cols": ["title", "service_type", "site_location", "scope_of_work"],
        "date_col": "created_at",
        "workspace_col": "workspace_id",
        "status_col": "status",
        "priority_col": None,
        "category_col": "service_type",
        "emp_col": None
    },
    "quotations": {
        "table": "business_quotations",
        "search_cols": ["quotation_number", "project_name", "terms"],
        "date_col": "created_at",
        "workspace_col": "workspace_id",
        "status_col": "status",
        "priority_col": None,
        "category_col": None,
        "emp_col": None
    },
    "work_orders": {
        "table": "business_work_orders",
        "search_cols": ["work_order_number", "title", "notes"],
        "date_col": "created_at",
        "workspace_col": "workspace_id",
        "status_col": "status",
        "priority_col": None,
        "category_col": None,
        "emp_col": "assigned_team_leader_id"
    },
    "invoices": {
        "table": "business_invoices",
        "search_cols": ["invoice_number"],
        "date_col": "invoice_date",
        "workspace_col": "workspace_id",
        "status_col": "status",
        "priority_col": None,
        "category_col": "payment_status",
        "emp_col": None
    },
    "expenses": {
        "table": "expense_claims",
        "search_cols": ["category", "notes", "project_id"],
        "date_col": "submitted_at",
        "workspace_col": "workspace_id",
        "status_col": "status",
        "priority_col": None,
        "category_col": "category",
        "emp_col": "employee_id"
    },
    "leads": {
        "table": "social_leads",
        "search_cols": ["lead_name", "company", "phone", "email", "service_interest"],
        "date_col": "created_at",
        "workspace_col": "workspace_id",
        "status_col": "lead_status",
        "priority_col": "lead_priority",
        "category_col": "service_interest",
        "emp_col": "assigned_employee_id"
    },
    "media": {
        "table": "social_media_assets",
        "search_cols": ["filename", "file_type", "resolution"],
        "date_col": "created_at",
        "workspace_col": "workspace_id",
        "status_col": "status",
        "priority_col": None,
        "category_col": "content_type",
        "emp_col": None
    },
    "studio": {
        "table": "studio_projects",
        "search_cols": ["title", "project_type", "aspect_ratio"],
        "date_col": "created_at",
        "workspace_col": "workspace_id",
        "status_col": "status",
        "priority_col": None,
        "category_col": "project_type",
        "emp_col": "created_by"
    },
    "clients": {
        "table": "social_client_profiles",
        "search_cols": ["company_name", "service_package"],
        "date_col": "created_at",
        "workspace_col": "workspace_id",
        "status_col": None,
        "priority_col": None,
        "category_col": "service_package",
        "emp_col": None
    }
}

ENTITY_ALIASES = {
    "workorders": "work_orders",
    "claims": "expenses",
    "logs": "media",
}

def normalize_entity(entity: str) -> str:
    return ENTITY_ALIASES.get(entity, entity)


def build_filtered_query(
    entity: str,
    workspace_id: str,
    filters: Dict[str, Any]
) -> Tuple[str, List[Any], str, List[Any], List[str]]:
    """Constructs base parameterized SQL, params, count SQL, count params, and active filter tags."""
    entity = normalize_entity(entity)
    cfg = TABLE_CONFIG.get(entity)
    if not cfg:
        raise ValueError(f"Unknown entity '{entity}' for universal filter.")

    tbl = cfg["table"]
    search_cols = cfg["search_cols"]
    date_col = cfg["date_col"]
    ws_col = cfg["workspace_col"]
    status_col = cfg.get("status_col")
    priority_col = cfg.get("priority_col")
    category_col = cfg.get("category_col")
    emp_col = cfg.get("emp_col")

    where_clauses: List[str] = []
    params: List[Any] = []
    active_tags: List[str] = []

    # 1. Workspace scope
    if workspace_id and workspace_id != "ALL":
        where_clauses.append(f"{tbl}.{ws_col} = ?")
        params.append(workspace_id)
        active_tags.append(f"Workspace: {workspace_id}")

    # 2. Text Search
    search_val = (filters.get("search") or filters.get("q") or "").strip()
    if search_val:
        search_terms = search_val.split()
        sub_clauses = []
        for term in search_terms:
            col_clauses = [f"{tbl}.{col} LIKE ?" for col in search_cols]
            sub_clauses.append(f"({' OR '.join(col_clauses)})")
            for _ in search_cols:
                params.append(f"%{term}%")
        where_clauses.append(" AND ".join(sub_clauses))
        active_tags.append(f"Search: '{search_val}'")

    # 3. Status filter
    status = (filters.get("status") or "").strip()
    if status and status.lower() != "all" and status_col:
        where_clauses.append(f"{tbl}.{status_col} = ?")
        params.append(status)
        active_tags.append(f"Status: {status}")

    # 4. Priority filter (if applicable)
    priority = (filters.get("priority") or "").strip()
    if priority and priority.lower() != "all" and priority_col:
        where_clauses.append(f"{tbl}.{priority_col} = ?")
        params.append(priority)
        active_tags.append(f"Priority: {priority}")

    # 5. Category filter
    category = (filters.get("category") or "").strip()
    if category and category.lower() != "all" and category_col:
        where_clauses.append(f"{tbl}.{category_col} = ?")
        params.append(category)
        active_tags.append(f"Category: {category}")

    # 6. Assigned Employee / User filter
    emp_id = filters.get("employee_id") or filters.get("assigned_to")
    if emp_id and str(emp_id).isdigit() and emp_col:
        where_clauses.append(f"{tbl}.{emp_col} = ?")
        params.append(int(emp_id))
        active_tags.append(f"Employee ID: {emp_id}")

    # 7. Date Range (from_date, to_date)
    from_date = (filters.get("from_date") or "").strip()
    if from_date and date_col:
        where_clauses.append(f"date({tbl}.{date_col}) >= date(?)")
        params.append(from_date)
        active_tags.append(f"From: {from_date}")

    to_date = (filters.get("to_date") or "").strip()
    if to_date and date_col:
        where_clauses.append(f"date({tbl}.{date_col}) <= date(?)")
        params.append(to_date)
        active_tags.append(f"To: {to_date}")

    # 8. Project ID
    proj_id = (filters.get("project_id") or "").strip()
    if proj_id and entity in ["tasks", "expenses"]:
        where_clauses.append(f"{tbl}.project_id = ?")
        params.append(proj_id)
        active_tags.append(f"Project: {proj_id}")

    where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    count_sql = f"SELECT COUNT(*) AS c FROM {tbl}{where_str}"
    count_params = list(params)

    base_sql = f"SELECT * FROM {tbl}{where_str}"
    return base_sql, params, count_sql, count_params, active_tags


def query_filtered_records(
    store: Store,
    entity: str,
    workspace_id: str,
    filters: Dict[str, Any],
    page: int = 1,
    limit: int = 20,
    sort_by: Optional[str] = None,
    sort_dir: str = "DESC"
) -> Dict[str, Any]:
    """Executes filtered search with database pagination and metadata."""
    entity = normalize_entity(entity)
    base_sql, params, count_sql, count_params, active_tags = build_filtered_query(entity, workspace_id, filters)

    # Total count
    count_row = store.fetchone(count_sql, count_params)
    total_count = count_row["c"] if count_row else 0

    page = max(1, int(page))
    limit = max(1, min(100, int(limit)))
    total_pages = max(1, (total_count + limit - 1) // limit)
    offset = (page - 1) * limit

    # Sorting
    cfg = TABLE_CONFIG[entity]
    sort_dir = "ASC" if str(sort_dir).upper() == "ASC" else "DESC"
    order_col = sort_by if (sort_by and re.match(r"^[a-zA-Z0-9_]+$", sort_by)) else (cfg["date_col"] or "id")

    sql = f"{base_sql} ORDER BY {order_col} {sort_dir} LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = store.fetchall(sql, params)

    return {
        "ok": True,
        "entity": entity,
        "workspace_id": workspace_id,
        "records": rows,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "limit": limit,
            "total_count": total_count,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "active_filters": active_tags,
        "filter_count": len(active_tags)
    }


def export_filtered_csv(
    store: Store,
    entity: str,
    workspace_id: str,
    filters: Dict[str, Any]
) -> Tuple[str, str]:
    """Generates standard CSV content from filtered query results."""
    entity = normalize_entity(entity)
    base_sql, params, _, _, _ = build_filtered_query(entity, workspace_id, filters)
    
    cfg = TABLE_CONFIG[entity]
    order_col = cfg["date_col"] or "id"
    sql = f"{base_sql} ORDER BY {order_col} DESC LIMIT 2000"
    rows = store.fetchall(sql, params)

    output = io.StringIO()
    if rows:
        headers = list(rows[0].keys())
        clean_headers = [h for h in headers if not h.endswith(("_json", "_metadata"))]
        writer = csv.DictWriter(output, fieldnames=clean_headers, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(dict(r))
    else:
        writer = csv.writer(output)
        writer.writerow(["status", "message"])
        writer.writerow(["empty", "No records matched the filter criteria"])

    date_str = datetime.now(KOLKATA_TZ).strftime("%Y%m%d_%H%M%S")
    filename = f"{entity}_export_{workspace_id}_{date_str}.csv"
    return output.getvalue(), filename
