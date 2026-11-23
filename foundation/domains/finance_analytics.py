# -*- coding: utf-8 -*-
"""SHAH GROUP AI OS — Multi-Period Financial Analytics & Expense Tracking Engine.

Provides:
  1. Weekly Financial Outflows & Inflows (Last 8 Weeks breakdown).
  2. Monthly P&L, Expense Claims, Payroll, and Operating Margin (Last 12 Months).
  3. Yearly Annual Financial Overview (Current & Historical Financial Years).
  4. Expense Category Distribution (Equipment, Fuel/Site Travel, Consumables, Labor, Marketing).
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List

KOLKATA_TZ = timezone(timedelta(hours=5, minutes=30))


def now_kolkata() -> datetime:
    return datetime.now(KOLKATA_TZ)


def now_kolkata_iso() -> str:
    return now_kolkata().strftime("%Y-%m-%d %H:%M:%S")


def get_multi_period_financial_breakdown(conn: sqlite3.Connection, workspace_id: str = "SSC") -> Dict[str, Any]:
    """Computes weekly, monthly, yearly financial breakdowns and expense category distributions."""
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Monthly Financial History (Last 12 Months)
    monthly_data = []
    current_date = now_kolkata()
    for i in range(11, -1, -1):
        # Calculate year and month
        y = current_date.year
        m = current_date.month - i
        while m <= 0:
            m += 12
            y -= 1
        month_str = f"{y:04d}-{m:02d}"
        month_label = datetime(y, m, 1).strftime("%b %Y")

        # Invoiced in this month
        cur.execute(
            """
            SELECT COALESCE(SUM(total_amount), 0), COALESCE(SUM(amount_paid), 0), COUNT(id)
            FROM business_invoices
            WHERE workspace_id = ? AND (invoice_date LIKE ? OR created_at LIKE ?) AND status != 'cancelled'
            """,
            (workspace_id, f"{month_str}%", f"{month_str}%")
        )
        inv_row = cur.fetchone()
        invoiced = float(inv_row[0]) if inv_row else 0.0
        collected = float(inv_row[1]) if inv_row else 0.0
        inv_count = int(inv_row[2]) if inv_row else 0

        # Expenses in this month
        cur.execute(
            """
            SELECT COALESCE(SUM(amount), 0), COUNT(id)
            FROM expense_claims
            WHERE workspace_id = ? AND (submitted_at LIKE ? OR created_at LIKE ?) AND status IN ('approved', 'settled')
            """,
            (workspace_id, f"{month_str}%", f"{month_str}%")
        )
        exp_row = cur.fetchone()
        expenses = float(exp_row[0]) if exp_row else 0.0
        exp_count = int(exp_row[1]) if exp_row else 0

        # Payroll in this month
        cur.execute(
            """
            SELECT COALESCE(SUM(total_gross), 0), COUNT(id)
            FROM payroll_runs
            WHERE workspace_id = ? AND (run_month LIKE ? OR created_at LIKE ?) AND status = 'approved'
            """,
            (workspace_id, f"{month_str}%", f"{month_str}%")
        )
        pay_row = cur.fetchone()
        payroll = float(pay_row[0]) if pay_row else 0.0

        total_outflow = round(expenses + payroll, 2)
        net_profit = round(collected - total_outflow, 2)
        margin_pct = round((net_profit / collected * 100), 1) if collected > 0 else 0.0

        monthly_data.append({
            "month_key": month_str,
            "month_label": month_label,
            "invoiced": invoiced,
            "collected": collected,
            "expenses": expenses,
            "payroll": payroll,
            "total_outflow": total_outflow,
            "net_profit": net_profit,
            "margin_pct": margin_pct,
            "invoice_count": inv_count,
            "expense_count": exp_count
        })

    # 2. Weekly Financial Outflows (Last 8 Weeks)
    weekly_data = []
    for w in range(7, -1, -1):
        end_dt = current_date - timedelta(days=w * 7)
        start_dt = end_dt - timedelta(days=6)
        s_str = start_dt.strftime("%Y-%m-%d")
        e_str = end_dt.strftime("%Y-%m-%d")
        w_label = f"{start_dt.strftime('%d %b')} - {end_dt.strftime('%d %b')}"

        cur.execute(
            """
            SELECT COALESCE(SUM(amount_paid), 0)
            FROM business_invoices
            WHERE workspace_id = ? AND date(invoice_date) BETWEEN date(?) AND date(?) AND status != 'cancelled'
            """,
            (workspace_id, s_str, e_str)
        )
        w_col = float(cur.fetchone()[0] or 0.0)

        cur.execute(
            """
            SELECT COALESCE(SUM(amount), 0), COUNT(id)
            FROM expense_claims
            WHERE workspace_id = ? AND date(COALESCE(submitted_at, created_at)) BETWEEN date(?) AND date(?) AND status IN ('approved', 'settled')
            """,
            (workspace_id, s_str, e_str)
        )
        w_exp_row = cur.fetchone()
        w_exp = float(w_exp_row[0] or 0.0)
        w_cnt = int(w_exp_row[1] or 0)

        weekly_data.append({
            "week_label": w_label,
            "start_date": s_str,
            "end_date": e_str,
            "inflow_collected": w_col,
            "expenses": w_exp,
            "net_cashflow": round(w_col - w_exp, 2),
            "claim_count": w_cnt
        })

    # 3. Yearly Financial Breakdown (Last 3 Years)
    yearly_data = []
    for y in [current_date.year - 2, current_date.year - 1, current_date.year]:
        y_str = f"{y}"

        cur.execute(
            """
            SELECT COALESCE(SUM(total_amount), 0), COALESCE(SUM(amount_paid), 0), COUNT(id)
            FROM business_invoices
            WHERE workspace_id = ? AND (invoice_date LIKE ? OR created_at LIKE ?) AND status != 'cancelled'
            """,
            (workspace_id, f"{y_str}%", f"{y_str}%")
        )
        y_inv_row = cur.fetchone()
        y_inv = float(y_inv_row[0] or 0.0)
        y_col = float(y_inv_row[1] or 0.0)

        cur.execute(
            """
            SELECT COALESCE(SUM(amount), 0), COUNT(id)
            FROM expense_claims
            WHERE workspace_id = ? AND (submitted_at LIKE ? OR created_at LIKE ?) AND status IN ('approved', 'settled')
            """,
            (workspace_id, f"{y_str}%", f"{y_str}%")
        )
        y_exp = float(cur.fetchone()[0] or 0.0)

        cur.execute(
            """
            SELECT COALESCE(SUM(total_gross), 0)
            FROM payroll_runs
            WHERE workspace_id = ? AND (run_month LIKE ? OR created_at LIKE ?) AND status = 'approved'
            """,
            (workspace_id, f"{y_str}%", f"{y_str}%")
        )
        y_pay = float(cur.fetchone()[0] or 0.0)

        y_outflow = round(y_exp + y_pay, 2)
        y_profit = round(y_col - y_outflow, 2)
        y_margin = round((y_profit / y_col * 100), 1) if y_col > 0 else 0.0

        yearly_data.append({
            "year": y,
            "year_label": f"FY {y}",
            "total_invoiced": y_inv,
            "total_collected": y_col,
            "total_expenses": y_exp,
            "total_payroll": y_pay,
            "total_outflow": y_outflow,
            "net_profit": y_profit,
            "profit_margin_pct": y_margin
        })

    # 4. Expense Category Breakdown (All-Time for Workspace)
    cur.execute(
        """
        SELECT COALESCE(category, 'General Operations') AS cat,
               COALESCE(SUM(amount), 0) AS total_amt,
               COUNT(id) AS claim_cnt
        FROM expense_claims
        WHERE workspace_id = ? AND status IN ('approved', 'settled')
        GROUP BY category
        ORDER BY total_amt DESC
        """,
        (workspace_id,)
    )
    cat_rows = cur.fetchall()
    categories = []
    total_cat_spend = sum(float(r["total_amt"]) for r in cat_rows) if cat_rows else 0.0

    for r in cat_rows:
        amt = float(r["total_amt"])
        pct = round((amt / total_cat_spend * 100), 1) if total_cat_spend > 0 else 0.0
        categories.append({
            "category": r["cat"],
            "amount": amt,
            "claim_count": int(r["claim_cnt"]),
            "share_percentage": pct
        })

    # If no categorized claims yet, provide standard structural categories
    if not categories:
        categories = [
            {"category": "Equipment Purchase & DGPS/Drone Maintenance", "amount": 0.0, "claim_count": 0, "share_percentage": 35.0},
            {"category": "Field Site Travel, Fuel & Vehicles", "amount": 0.0, "claim_count": 0, "share_percentage": 25.0},
            {"category": "Survey Consumables (Pillars, Pegs, CAD Prints)", "amount": 0.0, "claim_count": 0, "share_percentage": 15.0},
            {"category": "Sub-Contractors & Field Labor", "amount": 0.0, "claim_count": 0, "share_percentage": 15.0},
            {"category": "Office Admin, Software & Utilities", "amount": 0.0, "claim_count": 0, "share_percentage": 10.0}
        ]

    # Overall Summary
    total_collected_all = sum(m["collected"] for m in monthly_data)
    total_expenses_all = sum(m["expenses"] for m in monthly_data)
    total_payroll_all = sum(m["payroll"] for m in monthly_data)
    total_outflows_all = round(total_expenses_all + total_payroll_all, 2)
    net_operating_profit_all = round(total_collected_all - total_outflows_all, 2)

    return {
        "ok": True,
        "workspace_id": workspace_id,
        "generated_at": now_kolkata_iso(),
        "summary": {
            "total_collected": total_collected_all,
            "total_expenses": total_expenses_all,
            "total_payroll": total_payroll_all,
            "total_outflows": total_outflows_all,
            "net_operating_profit": net_operating_profit_all,
            "overall_profit_margin_pct": round((net_operating_profit_all / total_collected_all * 100), 1) if total_collected_all > 0 else 0.0
        },
        "weekly": weekly_data,
        "monthly": monthly_data,
        "yearly": yearly_data,
        "categories": categories
    }
