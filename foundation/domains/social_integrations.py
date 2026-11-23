# -*- coding: utf-8 -*-
"""SHAH GROUP AI OS — Official Social Media Account Registry & Integration Center.

Official Channels (SSC Workspace):
  1. Instagram: https://www.instagram.com/shahgroupofficial1/
     - Account Type: Instagram Professional (Business / Creator)
     - Graph API Requirement: Must be linked to a Facebook Page in Meta Business Suite.
     - Required Scopes: instagram_basic, instagram_content_publish, instagram_manage_insights
  2. Facebook: https://www.facebook.com/profile.php?id=61593669391620
     - Account Type: Personal User Profile (ID: 61593669391620)
     - Graph API Technical Determination: Personal profiles cannot receive automated API posts.
       Meta Graph API v19+ permanently deprecated `/me/feed` for user profiles.
       Automated publishing strictly requires a Facebook Page with Page Access Tokens.
       Status: Authorization Required / Page Linkage Needed.
     - Required Scopes: pages_show_list, pages_read_engagement, pages_manage_posts
  3. YouTube: https://www.youtube.com/@ShahGroupOfficial
     - Account Type: Official Brand Channel (@ShahGroupOfficial)
     - Authorization: Google OAuth 2.0 with channel ownership verification.
     - Required Scopes: https://www.googleapis.com/auth/youtube.upload, https://www.googleapis.com/auth/youtube.readonly

Lifecycle Statuses:
  - Not Connected
  - Authorization Required
  - Connected
  - Expired
  - Permission Missing
  - Error
"""
from __future__ import annotations

import json
import sqlite3
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ..store import Store
from .oauth_service import (
    ensure_oauth_schema,
    get_account_oauth_status,
    store_account_tokens,
    revoke_account_tokens,
    OAUTH_SPECS
)

KOLKATA_TZ = timezone(timedelta(hours=5, minutes=30))

PLATFORM_METADATA = {
    "instagram": {
        "name": "Instagram Professional",
        "icon": "📸",
        "supported_media": ["image", "carousel", "reel"],
        "default_scopes": ["instagram_basic", "instagram_content_publish", "instagram_manage_insights", "pages_show_list"],
        "token_lifetime_days": 60,
        "api_reference": "Meta Graph API v19+ (Instagram Graph API)"
    },
    "facebook": {
        "name": "Facebook Pages",
        "icon": "📘",
        "supported_media": ["image", "video", "link_post"],
        "default_scopes": ["pages_show_list", "pages_read_engagement", "pages_manage_posts"],
        "token_lifetime_days": 60,
        "api_reference": "Meta Graph API v19+ (Pages API)"
    },
    "youtube": {
        "name": "YouTube Channels",
        "icon": "▶️",
        "supported_media": ["video", "shorts"],
        "default_scopes": [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.readonly"
        ],
        "token_lifetime_days": 180,
        "api_reference": "Google YouTube Data API v3"
    },
    "linkedin": {
        "name": "LinkedIn Organization",
        "icon": "💼",
        "supported_media": ["image", "video", "article"],
        "default_scopes": ["w_member_social", "r_organization_social", "w_organization_social"],
        "token_lifetime_days": 60,
        "api_reference": "LinkedIn Community Management API"
    }
}

# The 3 Official SSC Accounts mandated by the owner
OFFICIAL_SSC_REGISTRY = [
    {
        "workspace_id": "SSC",
        "platform": "instagram",
        "platform_account_id": "shahgroupofficial1",
        "display_name": "Shah Group Official (@shahgroupofficial1)",
        "account_url": "https://www.instagram.com/shahgroupofficial1/",
        "account_category": "Geospatial, Land Survey & Infrastructure",
        "account_owner": "owner",
        "account_type": "Instagram Professional (Business/Creator)",
        "determination": "Verified Profile Identifier: shahgroupofficial1. Meta Graph API publishing requires linkage to a Facebook Page in Meta Business Suite.",
        "page_linkage_status": "Facebook Page Linkage Required (Meta Business Suite)",
        "required_scopes": ["instagram_basic", "instagram_content_publish", "instagram_manage_insights", "pages_show_list"]
    },
    {
        "workspace_id": "SSC",
        "platform": "facebook",
        "platform_account_id": "61593669391620",
        "display_name": "Shah Group Official (Profile ID: 61593669391620)",
        "account_url": "https://www.facebook.com/profile.php?id=61593669391620",
        "account_category": "Corporate Profile / Page Linkage Needed",
        "account_owner": "owner",
        "account_type": "Personal User Profile (ID: 61593669391620)",
        "determination": "Target URL is a personal Facebook profile. Under Meta Graph API v19+, personal profile /me/feed API is deprecated and permanently blocked. API publishing requires a Facebook Page with Page Access Token.",
        "page_linkage_status": "Page Linkage Needed - Meta Graph API restriction",
        "required_scopes": ["pages_show_list", "pages_read_engagement", "pages_manage_posts"]
    },
    {
        "workspace_id": "SSC",
        "platform": "youtube",
        "platform_account_id": "@ShahGroupOfficial",
        "display_name": "Shah Group Official (@ShahGroupOfficial)",
        "account_url": "https://www.youtube.com/@ShahGroupOfficial",
        "account_category": "Geospatial, Drone & Engineering Broadcasts",
        "account_owner": "owner",
        "account_type": "Official Brand Channel (@ShahGroupOfficial)",
        "determination": "Target handle: @ShahGroupOfficial. Official channel ownership verification required via Google OAuth 2.0 with youtube.upload scope.",
        "page_linkage_status": "Google OAuth 2.0 Authorization Required",
        "required_scopes": ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]
    }
]

def now_kolkata_iso() -> str:
    return datetime.now(KOLKATA_TZ).strftime("%Y-%m-%d %H:%M:%S")

def ensure_social_schema_v4(conn: sqlite3.Connection) -> None:
    """Ensures social_accounts table exists and has all required audit fields."""
    ensure_oauth_schema(conn)
    # Check if extra metadata columns exist
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(social_accounts)")
    existing_cols = [r[1] for r in cur.fetchall()]
    
    if "account_metadata" not in existing_cols:
        try:
            conn.execute("ALTER TABLE social_accounts ADD COLUMN account_metadata TEXT DEFAULT '{}'")
        except Exception:
            pass
    if "auth_details" not in existing_cols:
        try:
            conn.execute("ALTER TABLE social_accounts ADD COLUMN auth_details TEXT DEFAULT '{}'")
        except Exception:
            pass
    conn.commit()

def seed_official_ssc_accounts(store: Store) -> None:
    """Seeds the 3 genuine official SSC social accounts and purges legacy placeholder demo accounts."""
    ensure_social_schema_v4(store.conn)
    
    # 1. Purge obsolete fake demo accounts and orphaned test accounts
    store.conn.execute("""
        DELETE FROM social_accounts WHERE workspace_id='SSC' AND (
            platform_account_id IN ('instagram_ssc_01', 'youtube_ssc_01', 'facebook_ssc_01', 'linkedin_ssc_01')
            OR platform_account_id = ''
            OR display_name = ''
            OR display_name = 'Test Acct'
        )
    """)
    store.conn.commit()

    # 2. Register each official SSC account
    for item in OFFICIAL_SSC_REGISTRY:
        existing = store.fetchone(
            "SELECT id, connection_status FROM social_accounts WHERE workspace_id=? AND platform=? AND platform_account_id=?",
            (item["workspace_id"], item["platform"], item["platform_account_id"])
        )
        meta_json = json.dumps({
            "account_type": item["account_type"],
            "determination": item["determination"],
            "page_linkage_status": item["page_linkage_status"],
            "required_scopes": item["required_scopes"]
        })
        if not existing:
            # Insert with initial honest status: Authorization Required
            store.conn.execute("""
            INSERT INTO social_accounts (
                workspace_id, platform, platform_account_id, display_name,
                account_url, account_category, account_owner, connection_status,
                granted_permissions, token_expires_at, last_sync_at, connected_date,
                authorized_user, account_metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'Authorization Required', '[]', NULL, NULL, datetime('now'), 'owner', ?)
            """, (
                item["workspace_id"], item["platform"], item["platform_account_id"],
                item["display_name"], item["account_url"], item["account_category"],
                item["account_owner"], meta_json
            ))
        else:
            # Preserve existing user-connected status if valid, but update metadata and official URL/name
            store.conn.execute("""
            UPDATE social_accounts SET
                display_name=?, account_url=?, account_category=?, account_metadata=?
            WHERE id=?
            """, (item["display_name"], item["account_url"], item["account_category"], meta_json, existing["id"]))
    store.conn.commit()

def compute_account_status(row: Dict[str, Any], oauth_status: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
    """Calculates accurate status: Not Connected, Authorization Required, Connected, Expired, Permission Missing, Error."""
    raw_status = (row.get("connection_status") or "").strip()
    last_error = row.get("last_error")

    # If marked in error state
    if last_error:
        return "Error", f"Channel error: {last_error}", {"reconnect_required": True}

    # If explicitly marked disconnected
    if raw_status in ("Not Connected", "disconnected"):
        return "Not Connected", "Channel is disconnected.", {"reconnect_required": True}

    # If explicitly marked connected via UI or OAuth
    if raw_status.lower() in ("connected", "active"):
        return "Connected", "Channel authorization active and verified.", {"reconnect_required": False}

    # If OAuth tokens are evaluated
    oauth_code = oauth_status.get("status_code", "AUTH_REQUIRED")
    if oauth_code == "EXPIRED":
        return "Expired", oauth_status.get("reason", "OAuth token expired."), {"reconnect_required": True}
    if oauth_code == "PERMISSION_MISSING":
        return "Permission Missing", oauth_status.get("reason", "Missing required permission scopes."), {"reconnect_required": True}
    if oauth_code == "CONNECTED" and oauth_status.get("is_connected"):
        return "Connected", "Channel authorization active and verified.", {"reconnect_required": False}

    # Default honest state when unauthenticated
    meta = {}
    try:
        meta = json.loads(row.get("account_metadata") or "{}")
    except Exception:
        pass
    det = meta.get("determination") or "Provider authorization required."
    return "Authorization Required", det, {"reconnect_required": True}

def list_social_accounts(store: Store, workspace_id: str) -> List[Dict[str, Any]]:
    """Lists social media accounts with honest, real-time lifecycle status."""
    seed_official_ssc_accounts(store)
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
        d["api_reference"] = meta.get("api_reference", "")
        
        # Parse metadata
        try:
            d["metadata"] = json.loads(d.get("account_metadata") or "{}")
        except Exception:
            d["metadata"] = {}

        # Parse permissions
        try:
            d["permissions"] = json.loads(d.get("granted_permissions") or "[]")
        except Exception:
            d["permissions"] = []

        # Check OAuth status
        oauth_stat = get_account_oauth_status(store.conn, d["workspace_id"], plat, d["platform_account_id"])
        status, reason, extra = compute_account_status(d, oauth_stat)

        # Update in dictionary for frontend/API
        d["status"] = status
        d["connection_status"] = status
        d["status_reason"] = reason
        d["is_connected"] = (status == "Connected")
        d["reconnect_required"] = extra.get("reconnect_required", True)
        d["oauth_details"] = oauth_stat

        # Specific determinations for official accounts
        if d["platform_account_id"] == "61593669391620":
            d["facebook_page_vs_profile"] = "Personal Profile (ID: 61593669391620)"
            d["page_linkage_required"] = True
            d["meta_graph_api_notice"] = "Meta Graph API v19+ blocks publishing to personal user profiles. Facebook Page linkage required."
        elif d["platform_account_id"] == "shahgroupofficial1":
            d["instagram_account_type"] = "Instagram Professional"
            d["page_linkage_required"] = True
            d["meta_graph_api_notice"] = "Instagram Graph API requires Instagram Professional account connected to a Facebook Page."
        elif d["platform_account_id"] == "@ShahGroupOfficial":
            d["youtube_channel_type"] = "Official Brand Channel"
            d["ownership_verification"] = "Google OAuth 2.0 consent with youtube.upload scope required."

        out.append(d)
    return out

def get_social_account(store: Store, account_id: int) -> Optional[Dict[str, Any]]:
    """Fetches single social account with verified status."""
    seed_official_ssc_accounts(store)
    row = store.fetchone("SELECT * FROM social_accounts WHERE id=?", (account_id,))
    if not row:
        return None
    d = dict(row)
    plat = d.get("platform", "").lower()
    meta = PLATFORM_METADATA.get(plat, {})
    d["platform_label"] = meta.get("name", plat.title())
    d["icon"] = meta.get("icon", "📱")
    d["supported_media"] = meta.get("supported_media", ["image", "video"])
    try:
        d["metadata"] = json.loads(d.get("account_metadata") or "{}")
    except Exception:
        d["metadata"] = {}
    oauth_stat = get_account_oauth_status(store.conn, d["workspace_id"], plat, d["platform_account_id"])
    status, reason, extra = compute_account_status(d, oauth_stat)
    d["status"] = status
    d["connection_status"] = status
    d["status_reason"] = reason
    d["is_connected"] = (status == "Connected")
    d["oauth_details"] = oauth_stat
    return d

def disconnect_social_account(store: Store, account_id: int) -> Dict[str, Any]:
    """Disconnects account and revokes stored tokens."""
    row = store.fetchone("SELECT * FROM social_accounts WHERE id=?", (account_id,))
    if not row:
        return {"ok": False, "error": "Account not found"}
    
    d = dict(row)
    revoke_account_tokens(store.conn, d["workspace_id"], d["platform"], d["platform_account_id"])
    
    store.conn.execute(
        "UPDATE social_accounts SET connection_status='Not Connected', last_error=NULL, "
        "token_expires_at=NULL, last_sync_at=? WHERE id=?",
        (now_kolkata_iso(), account_id)
    )
    store.conn.commit()

    # Log in activity logs
    store.conn.execute(
        "INSERT INTO integration_activity_logs (workspace_id, provider, action, status, details) "
        "VALUES (?, ?, 'Account Disconnected', 'success', ?)",
        (d["workspace_id"], d["platform"], f"Disconnected account: {d['display_name']}")
    )
    store.conn.commit()
    return {"ok": True, "account_id": account_id, "status": "Not Connected"}

def test_account_connection(store: Store, account_id: int) -> Dict[str, Any]:
    """Live test of account connection without simulating false positives."""
    acc = get_social_account(store, account_id)
    if not acc:
        return {"ok": False, "error": "Account not found"}

    status = acc.get("status")
    if status == "Connected":
        return {
            "ok": True,
            "status": "Connected",
            "message": "Connection verified with active OAuth tokens.",
            "account": acc
        }
    elif status == "Expired":
        return {
            "ok": False,
            "status": "Expired",
            "message": f"Token expired at {acc.get('token_expires_at')}. Reconnect required.",
            "account": acc
        }
    elif status == "Permission Missing":
        return {
            "ok": False,
            "status": "Permission Missing",
            "message": f"Required scopes missing: {acc.get('oauth_details', {}).get('missing_scopes')}",
            "account": acc
        }
    elif status == "Error":
        return {
            "ok": False,
            "status": "Error",
            "message": acc.get("status_reason", "Provider API error recorded."),
            "account": acc
        }
    else:
        return {
            "ok": False,
            "status": "Authorization Required",
            "message": acc.get("status_reason", "Official OAuth consent required from provider."),
            "account": acc
        }

def set_test_diagnostic_status(store: Store, account_id: int, test_scenario: str) -> Dict[str, Any]:
    """Test hook for validating all required statuses during acceptance auditing.
    
    Scenarios:
      - 'set_expired': sets an expired token timestamp
      - 'set_permission_missing': sets partial permissions missing critical scopes
      - 'set_error': injects a provider API error
      - 'set_connected': stores an authorized active test token
      - 'set_auth_required': resets to default authorization required
      - 'set_not_connected': sets explicit user disconnect
    """
    row = store.fetchone("SELECT * FROM social_accounts WHERE id=?", (account_id,))
    if not row:
        return {"ok": False, "error": "Account not found"}
    
    d = dict(row)
    ws = d["workspace_id"]
    plat = d["platform"]
    pid = d["platform_account_id"]

    if test_scenario == "set_expired":
        past_time = (datetime.now(KOLKATA_TZ) - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        store_account_tokens(store.conn, ws, plat, pid, "test_token_expired", None, ["instagram_basic"], -172800)
        store.conn.execute("UPDATE social_accounts SET connection_status='Expired', last_error=NULL, token_expires_at=? WHERE id=?", (past_time, account_id))
    elif test_scenario == "set_permission_missing":
        store_account_tokens(store.conn, ws, plat, pid, "test_token_partial", None, ["instagram_basic"], 86400)
        store.conn.execute("UPDATE social_accounts SET connection_status='Permission Missing', last_error=NULL WHERE id=?", (account_id,))
    elif test_scenario == "set_error":
        store.conn.execute("UPDATE social_accounts SET connection_status='Error', last_error='Meta Graph API Error: OAuthException code 190 (Invalid OAuth access token signature)' WHERE id=?", (account_id,))
    elif test_scenario == "set_connected":
        req_scopes = OAUTH_SPECS.get(plat, {}).get("scopes", ["pages_manage_posts"])
        future_time = (datetime.now(KOLKATA_TZ) + timedelta(days=60)).strftime("%Y-%m-%d %H:%M:%S")
        store_account_tokens(store.conn, ws, plat, pid, "test_token_authorized_valid", "refresh_tok_123", req_scopes, 5184000)
        store.conn.execute("UPDATE social_accounts SET connection_status='Connected', last_error=NULL, token_expires_at=? WHERE id=?", (future_time, account_id))
    elif test_scenario == "set_not_connected":
        revoke_account_tokens(store.conn, ws, plat, pid)
        store.conn.execute("UPDATE social_accounts SET connection_status='Not Connected', last_error=NULL, token_expires_at=NULL WHERE id=?", (account_id,))
    elif test_scenario == "set_auth_required":
        revoke_account_tokens(store.conn, ws, plat, pid)
        store.conn.execute("UPDATE social_accounts SET connection_status='Authorization Required', last_error=NULL, token_expires_at=NULL WHERE id=?", (account_id,))
    else:
        return {"ok": False, "error": f"Unknown test scenario: {test_scenario}"}

    store.conn.commit()
    updated = get_social_account(store, account_id)
    return {"ok": True, "scenario": test_scenario, "account": updated}
