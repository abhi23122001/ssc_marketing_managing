# -*- coding: utf-8 -*-
"""SHAH GROUP AI OS — Social Media Integration & Account Management Center.

Supported Platforms:
  1. Instagram (Business / Creator Graph API)
  2. Facebook Pages (Meta Graph API)
  3. YouTube (YouTube Data v3 API)
  4. LinkedIn (Marketing & Community Management API)

Features:
  - Account connection lifecycle: Connect, Disconnect, Test Connection, Re-auth.
  - Multi-step publishing workflow:
      Draft -> Review -> Approval (Owner/Manager signoff) -> Schedule -> Publish.
  - Token validity and permission scope tracking.
  - Workspace scoping (SSC channels vs INFRA channels).
"""
from __future__ import annotations

import json
import sqlite3
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ..store import Store

KOLKATA_TZ = timezone(timedelta(hours=5, minutes=30))

PLATFORM_METADATA = {
    "instagram": {
        "name": "Instagram",
        "icon": "📸",
        "supported_media": ["image", "carousel", "reel"],
        "default_scopes": ["instagram_basic", "instagram_content_publish", "instagram_manage_insights"],
        "token_lifetime_days": 60
    },
    "facebook": {
        "name": "Facebook Pages",
        "icon": "📘",
        "supported_media": ["image", "video", "link_post"],
        "default_scopes": ["pages_show_list", "pages_read_engagement", "pages_manage_posts"],
        "token_lifetime_days": 60
    },
    "youtube": {
        "name": "YouTube",
        "icon": "▶️",
        "supported_media": ["video", "shorts"],
        "default_scopes": ["youtube.upload", "youtube.readonly"],
        "token_lifetime_days": 180
    },
    "linkedin": {
        "name": "LinkedIn",
        "icon": "💼",
        "supported_media": ["image", "video", "article"],
        "default_scopes": ["w_member_social", "r_organization_social", "w_organization_social"],
        "token_lifetime_days": 60
    }
}


def now_kolkata_iso() -> str:
    return datetime.now(KOLKATA_TZ).strftime("%Y-%m-%d %H:%M:%S")


def ensure_social_accounts_seeded(store: Store) -> None:
    """Pre-seeds standard authorized business channels for SSC and INFRA."""
    default_accounts = [
        # SSC Accounts
        ("SSC", "instagram", "instagram_ssc_01", "Shah Surveyors & Consultancy (@shah_surveyors)",
         "https://instagram.com/shah_surveyors", "Geospatial Consulting", "connected",
         ["instagram_basic", "instagram_content_publish", "instagram_manage_insights"], 4200),
        ("SSC", "youtube", "youtube_ssc_01", "Shah Geospatial & Survey Tech",
         "https://youtube.com/@shah_surveyors", "Technical Training & Site Demos", "connected",
         ["youtube.upload", "youtube.readonly"], 1850),
        ("SSC", "linkedin", "linkedin_ssc_01", "Shah Surveyors and Consultancy",
         "https://linkedin.com/company/shah-surveyors", "B2B Infrastructure", "connected",
         ["w_member_social", "r_organization_social"], 2100),
        ("SSC", "facebook", "facebook_ssc_01", "Shah Surveyors & Consultancy",
         "https://facebook.com/shahsurveyors", "Official Business Page", "connected",
         ["pages_show_list", "pages_manage_posts"], 3400),

        # INFRA Accounts
        ("INFRA", "instagram", "instagram_inf_01", "Shah Infra Developers (@shah_infra_developers)",
         "https://instagram.com/shah_infra_developers", "Civil & Highway Contracting", "connected",
         ["instagram_basic", "instagram_content_publish"], 2800),
        ("INFRA", "facebook", "facebook_inf_01", "Shah Infra Developers Pvt Ltd",
         "https://facebook.com/shahinfradevelopers", "Construction & Earthworks", "connected",
         ["pages_show_list", "pages_manage_posts"], 4500),
        ("INFRA", "linkedin", "linkedin_inf_01", "Shah Infra Developers",
         "https://linkedin.com/company/shah-infra-developers", "Civil Engineering & EPC", "connected",
         ["w_member_social", "r_organization_social"], 1650),
        ("INFRA", "youtube", "youtube_inf_01", "Shah Infra Highway Construction",
         "https://youtube.com/@shah_infra", "Heavy Machinery & Road Projects", "connected",
         ["youtube.upload"], 920)
    ]

    for ws, plat, pid, name, url, cat, status, scopes, followers in default_accounts:
        existing = store.fetchone(
            "SELECT id FROM social_accounts WHERE workspace_id=? AND platform=? AND platform_account_id=?",
            (ws, plat, pid)
        )
        if not existing:
            store.conn.execute(
                "INSERT INTO social_accounts (workspace_id, platform, platform_account_id, display_name, "
                "account_url, account_category, connection_status, granted_permissions, token_expires_at, "
                "last_sync_at, connected_date, authorized_user) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'owner')",
                (ws, plat, pid, name, url, cat, status, json.dumps(scopes),
                 (datetime.now(KOLKATA_TZ) + timedelta(days=60)).strftime("%Y-%m-%d"),
                 now_kolkata_iso(), now_kolkata_iso())
            )
    store.conn.commit()


def list_social_accounts(store: Store, workspace_id: str) -> List[Dict[str, Any]]:
    """Lists connected channels for the current workspace with health status."""
    ensure_social_accounts_seeded(store)
    sql = "SELECT * FROM social_accounts WHERE workspace_id=?" if workspace_id != "ALL" else "SELECT * FROM social_accounts"
    params = [workspace_id] if workspace_id != "ALL" else []
    rows = store.fetchall(sql, params)
    
    out = []
    for r in rows:
        d = dict(r)
        plat = d.get("platform", "").lower()
        meta = PLATFORM_METADATA.get(plat, {})
        d["platform_label"] = meta.get("name", plat.title())
        d["icon"] = meta.get("icon", "📱")
        d["supported_media"] = meta.get("supported_media", ["image", "video"])
        try:
            d["permissions"] = json.loads(d.get("granted_permissions") or "[]")
        except Exception:
            d["permissions"] = []
        out.append(d)
    return out


def toggle_account_connection(store: Store, account_id: int, connect: bool = True) -> Dict[str, Any]:
    """Connects or disconnects a social media channel."""
    status = "connected" if connect else "disconnected"
    expires = (datetime.now(KOLKATA_TZ) + timedelta(days=60)).strftime("%Y-%m-%d") if connect else None
    store.conn.execute(
        "UPDATE social_accounts SET connection_status=?, token_expires_at=?, last_sync_at=? WHERE id=?",
        (status, expires, now_kolkata_iso(), account_id)
    )
    store.conn.commit()
    row = store.fetchone("SELECT * FROM social_accounts WHERE id=?", (account_id,))
    return dict(row) if row else {}


def sync_account_telemetry(store: Store, account_id: int) -> Dict[str, Any]:
    """Simulates real synchronization check with remote platform endpoint."""
    store.conn.execute(
        "UPDATE social_accounts SET last_sync_at=?, connection_status='connected', last_error=NULL WHERE id=?",
        (now_kolkata_iso(), account_id)
    )
    store.conn.commit()
    row = store.fetchone("SELECT * FROM social_accounts WHERE id=?", (account_id,))
    return {"ok": True, "account": dict(row) if row else {}, "synced_at": now_kolkata_iso()}


def get_social_publishing_pipeline(store: Store, workspace_id: str) -> Dict[str, Any]:
    """Returns content pieces organized by publishing workflow stages:
    
    Stages:
      - draft
      - in_review
      - approved
      - scheduled
      - published
    """
    sql = "SELECT * FROM social_content_items WHERE workspace_id=?" if workspace_id != "ALL" else "SELECT * FROM social_content_items"
    params = [workspace_id] if workspace_id != "ALL" else []
    items = store.fetchall(sql, params)

    pipeline = {
        "draft": [],
        "in_review": [],
        "approved": [],
        "scheduled": [],
        "published": []
    }

    for it in items:
        st = it.get("status", "draft")
        if st in pipeline:
            pipeline[st].append(dict(it))
        else:
            pipeline["draft"].append(dict(it))

    counts = {k: len(v) for k, v in pipeline.items()}
    return {"pipeline": pipeline, "counts": counts, "total_posts": len(items)}
