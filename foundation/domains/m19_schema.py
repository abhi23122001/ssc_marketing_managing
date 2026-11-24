"""M19 Social Media Marketing Department — SQLite schema + migrations.

Single source of truth for the M19 tables, added idempotently to the existing
foundation database. Nothing here is destructive: tables are created only if
absent, and no existing user data is touched.

Workspace isolation: every M19 table is owned by a business (`workspace_id`) or
an external client (`client_workspace_id`), and records are scoped accordingly.
No cross-workspace access without the Owner role.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

_DOMAIN_SCHEMA = _DOMAIN_SCHEMA_EN = """
CREATE TABLE IF NOT EXISTS social_workspaces (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    label TEXT NOT NULL,
    is_isolated INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS social_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    client_workspace_id TEXT,
    platform TEXT NOT NULL,
    platform_account_id TEXT NOT NULL DEFAULT '',
    display_name TEXT NOT NULL DEFAULT '',
    account_url TEXT NOT NULL DEFAULT '',
    account_category TEXT NOT NULL DEFAULT '',
    account_owner TEXT NOT NULL DEFAULT '',
    connection_status TEXT NOT NULL DEFAULT 'disconnected',
    granted_permissions TEXT NOT NULL DEFAULT '{}',
    token_expires_at TEXT,
    last_sync_at TEXT,
    last_failed_sync_at TEXT,
    last_error TEXT,
    connected_date TEXT NOT NULL DEFAULT (datetime('now')),
    authorized_user TEXT NOT NULL DEFAULT 'owner',
    UNIQUE(workspace_id, platform, platform_account_id),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (client_workspace_id) REFERENCES social_workspaces(id) ON DELETE SET NULL,
    CHECK (platform IN ('instagram','facebook','linkedin','youtube'))
);

CREATE TABLE IF NOT EXISTS social_account_syncs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'ok',
    scope TEXT NOT NULL DEFAULT 'ok',
    error TEXT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    FOREIGN KEY (account_id) REFERENCES social_accounts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_brand_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    client_workspace_id TEXT,
    business_name TEXT NOT NULL DEFAULT '',
    brand_voice TEXT NOT NULL DEFAULT '',
    tone TEXT NOT NULL DEFAULT '',
    brand_colors TEXT NOT NULL DEFAULT '{}',
    brand_logo_url TEXT NOT NULL DEFAULT '',
    service_locations TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(workspace_id, client_workspace_id),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (client_workspace_id) REFERENCES social_workspaces(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS social_brand_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL DEFAULT 'image',
    file_size INTEGER NOT NULL DEFAULT 0,
    checksum TEXT NOT NULL DEFAULT '',
    content_type TEXT NOT NULL DEFAULT 'image/png',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (brand_id) REFERENCES social_brand_profiles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_trends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    trend_title TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT '',
    discovery_date TEXT NOT NULL,
    relevance TEXT NOT NULL DEFAULT 'medium',
    audience_relevance TEXT NOT NULL DEFAULT 'medium',
    content_potential TEXT NOT NULL DEFAULT 'medium',
    freshness TEXT NOT NULL DEFAULT 'high',
    platform TEXT NOT NULL DEFAULT 'instagram',
    suggested_hook TEXT NOT NULL DEFAULT '',
    suggested_script TEXT NOT NULL DEFAULT '',
    suggested_audio TEXT NOT NULL DEFAULT '',
    audio_permission TEXT NOT NULL DEFAULT 'none',
    content_opportunity TEXT NOT NULL DEFAULT '',
    priority TEXT NOT NULL DEFAULT 'medium',
    expiry_date TEXT,
    reviewed_by TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_competitor_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    name TEXT NOT NULL DEFAULT '',
    display_name TEXT NOT NULL DEFAULT '',
    platform TEXT NOT NULL DEFAULT 'instagram',
    account_url TEXT NOT NULL DEFAULT '',
    category TEXT NOT NULL DEFAULT '',
    followers_fake INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_content_ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    client_workspace_id TEXT,
    pillar TEXT NOT NULL DEFAULT '',
    business TEXT NOT NULL DEFAULT '',
    platform TEXT NOT NULL DEFAULT 'instagram',
    objective TEXT NOT NULL DEFAULT '',
    target_audience TEXT NOT NULL DEFAULT '',
    journey_stage TEXT NOT NULL DEFAULT '',
    content_format TEXT NOT NULL DEFAULT 'reel',
    hook TEXT NOT NULL DEFAULT '',
    key_message TEXT NOT NULL DEFAULT '',
    cta TEXT NOT NULL DEFAULT '',
    keywords TEXT NOT NULL DEFAULT '[]',
    title TEXT NOT NULL DEFAULT '',
    duration_seconds REAL NOT NULL DEFAULT 0,
    required_media TEXT NOT NULL DEFAULT '[]',
    production_difficulty TEXT NOT NULL DEFAULT 'medium',
    expected_outcome TEXT NOT NULL DEFAULT '',
    success_metric TEXT NOT NULL DEFAULT '',
    priority TEXT NOT NULL DEFAULT 'medium',
    status TEXT NOT NULL DEFAULT 'idea',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    language TEXT NOT NULL DEFAULT 'en',
    script TEXT NOT NULL DEFAULT '',
    voiceover_text TEXT NOT NULL DEFAULT '',
    subtitle_text TEXT NOT NULL DEFAULT '',
    on_screen_text TEXT NOT NULL DEFAULT '[]',
    conversation_style TEXT NOT NULL DEFAULT 'professional',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (content_id) REFERENCES social_content_items(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_media_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL DEFAULT 'video',
    content_type TEXT NOT NULL DEFAULT 'video/mp4',
    duration_seconds REAL NOT NULL DEFAULT 0,
    resolution TEXT NOT NULL DEFAULT '',
    frame_rate TEXT NOT NULL DEFAULT '',
    has_audio INTEGER NOT NULL DEFAULT 0,
    checksum TEXT NOT NULL DEFAULT '',
    thumb_url TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_video_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    account_id INTEGER,
    input_asset_id INTEGER NOT NULL,
    output_asset_id INTEGER,
    status TEXT NOT NULL DEFAULT 'queued',
    script_id INTEGER,
    language TEXT NOT NULL DEFAULT 'en',
    duration_seconds REAL,
    aspect_ratio TEXT NOT NULL DEFAULT '9:16',
    status_detail TEXT NOT NULL DEFAULT '',
    queue_time TEXT,
    started_at TEXT,
    processing_time TEXT,
    completed_at TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES social_accounts(id) ON DELETE SET NULL,
    FOREIGN KEY (input_asset_id) REFERENCES social_media_assets(id) ON DELETE CASCADE,
    FOREIGN KEY (output_asset_id) REFERENCES social_media_assets(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS social_subtitles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_job_id INTEGER NOT NULL,
    language TEXT NOT NULL DEFAULT 'en',
    srt_text TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending',
    started_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (video_job_id) REFERENCES social_video_jobs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_thumbnails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    filename TEXT NOT NULL DEFAULT '',
    thumbnail_url TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (asset_id) REFERENCES social_media_assets(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_content_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    client_workspace_id TEXT,
    content_id TEXT NOT NULL DEFAULT '',
    pillar TEXT NOT NULL DEFAULT '',
    business TEXT NOT NULL DEFAULT '',
    platform TEXT NOT NULL DEFAULT 'instagram',
    content_format TEXT NOT NULL DEFAULT 'reel',
    objective TEXT NOT NULL DEFAULT '',
    target_audience TEXT NOT NULL DEFAULT '',
    journey_stage TEXT NOT NULL DEFAULT '',
    hook TEXT NOT NULL DEFAULT '',
    key_message TEXT NOT NULL DEFAULT '',
    cta TEXT NOT NULL DEFAULT '',
    keywords TEXT NOT NULL DEFAULT '[]',
    required_media TEXT NOT NULL DEFAULT '[]',
    title TEXT NOT NULL DEFAULT '',
    duration_seconds REAL NOT NULL DEFAULT 0,
    script TEXT NOT NULL DEFAULT '',
    caption TEXT NOT NULL DEFAULT '',
    voiceover_text TEXT NOT NULL DEFAULT '',
    subtitle_text TEXT NOT NULL DEFAULT '',
    thumbnail_text TEXT NOT NULL DEFAULT '',
    on_screen_text TEXT NOT NULL DEFAULT '[]',
    visual_direction TEXT NOT NULL DEFAULT '',
    production_difficulty TEXT NOT NULL DEFAULT 'medium',
    priority TEXT NOT NULL DEFAULT 'medium',
    expected_outcome TEXT NOT NULL DEFAULT '',
    success_metric TEXT NOT NULL DEFAULT '',
    assigned_employee_id INTEGER,
    calendar_version INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (client_workspace_id) REFERENCES social_workspaces(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS social_content_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    workflow_state TEXT NOT NULL DEFAULT 'idea',
    script TEXT NOT NULL DEFAULT '',
    caption TEXT NOT NULL DEFAULT '',
    cta TEXT NOT NULL DEFAULT '',
    keywords TEXT NOT NULL DEFAULT '[]',
    thumbnail_text TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'idea',
    version_note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (content_id) REFERENCES social_content_items(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_calendar_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    content_id INTEGER NOT NULL,
    platform TEXT NOT NULL DEFAULT 'instagram',
    publish_date TEXT NOT NULL DEFAULT '',
    publish_time TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'planning',
    assigned_employee_id INTEGER,
    internal_review_at TEXT,
    approval_deadline TEXT,
    publish_platform_account TEXT,
    publish_hook TEXT NOT NULL DEFAULT '',
    publish_caption TEXT NOT NULL DEFAULT '',
    publish_hashtags TEXT NOT NULL DEFAULT '[]',
    publish_media_url TEXT NOT NULL DEFAULT '',
    version_locked INTEGER NOT NULL DEFAULT 0,
    review_notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (content_id) REFERENCES social_content_items(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    content_id INTEGER NOT NULL,
    employee_id INTEGER,
    due_date TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'open', -- open, in_progress, done, blocked
    priority TEXT NOT NULL DEFAULT 'medium',
    assignee_notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (content_id) REFERENCES social_content_items(id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS social_approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    client_workspace_id TEXT,
    requester_id INTEGER NOT NULL,
    approver_ids TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'pending', -- pending, approved, rejected, withdrawn
    version_locked INTEGER NOT NULL DEFAULT 1,
    final_version INTEGER NOT NULL DEFAULT 0,
    final_script TEXT NOT NULL DEFAULT '',
    final_caption TEXT NOT NULL DEFAULT '',
    final_cta TEXT NOT NULL DEFAULT '',
    final_hashtags TEXT NOT NULL DEFAULT '[]',
    final_media_url TEXT NOT NULL DEFAULT '',
    approval_note TEXT NOT NULL DEFAULT '',
    approved_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (content_id) REFERENCES social_content_items(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_publish_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    content_id INTEGER NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    account_id INTEGER,
    client_workspace_id TEXT,
    platform TEXT NOT NULL DEFAULT 'instagram',
    publish_at TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'scheduled', -- scheduled, published, failed, reconciled
    job_url TEXT NOT NULL DEFAULT '',
    output_url TEXT NOT NULL DEFAULT '',
    platform_response TEXT NOT NULL DEFAULT '{}',
    error TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    last_attempt_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (content_id) REFERENCES social_content_items(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES social_accounts(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS social_published_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    account_id INTEGER NOT NULL,
    platform TEXT NOT NULL DEFAULT 'instagram',
    client_workspace_id TEXT,
    status TEXT NOT NULL DEFAULT 'published',
    post_url TEXT NOT NULL DEFAULT '',
    platform_post_id TEXT NOT NULL DEFAULT '',
    platform_status TEXT NOT NULL DEFAULT 'live',
    performance_summary TEXT NOT NULL DEFAULT '{}',
    published_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (account_id) REFERENCES social_accounts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    client_workspace_id TEXT,
    author TEXT NOT NULL DEFAULT '',
    body TEXT NOT NULL DEFAULT '',
    sentiment TEXT NOT NULL DEFAULT 'neutral',
    is_spam INTEGER NOT NULL DEFAULT 0,
    response_draft TEXT NOT NULL DEFAULT '',
    response_status TEXT NOT NULL DEFAULT 'draft', -- draft, sent, ignored
    assigned_employee_id INTEGER,
    reply_sent_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (account_id) REFERENCES social_accounts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    client_workspace_id TEXT,
    author TEXT NOT NULL DEFAULT '',
    body TEXT NOT NULL DEFAULT '',
    channel TEXT NOT NULL DEFAULT 'comment',
    sentiment TEXT NOT NULL DEFAULT 'neutral',
    intent_class TEXT NOT NULL DEFAULT '',
    response_draft TEXT NOT NULL DEFAULT '',
    response_status TEXT NOT NULL DEFAULT 'draft',
    assigned_employee_id INTEGER,
    reply_sent_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (account_id) REFERENCES social_accounts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    client_workspace_id TEXT,
    lead_name TEXT NOT NULL DEFAULT '',
    company TEXT NOT NULL DEFAULT '',
    phone TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    location TEXT NOT NULL DEFAULT '',
    platform TEXT NOT NULL DEFAULT 'instagram',
    source_post TEXT NOT NULL DEFAULT '',
    enquiry_text TEXT NOT NULL DEFAULT '',
    service_interest TEXT NOT NULL DEFAULT '',
    lead_priority TEXT NOT NULL DEFAULT 'medium',
    assigned_employee_id INTEGER,
    follow_up_date TEXT,
    lead_status TEXT NOT NULL DEFAULT 'new', -- new, qualified, in_progress, won, lost
    quotation_status TEXT NOT NULL DEFAULT 'none',
    conversion_status TEXT NOT NULL DEFAULT 'none',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (client_workspace_id) REFERENCES social_workspaces(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS social_lead_attribution (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER NOT NULL,
    source_event TEXT NOT NULL DEFAULT '',
    attribution_details TEXT NOT NULL DEFAULT '{}',
    captured_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (lead_id) REFERENCES social_leads(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_employee_kpis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    employee_id TEXT NOT NULL,
    role_code TEXT NOT NULL DEFAULT 'content_creator',
    video_assigned INTEGER NOT NULL DEFAULT 0,
    videos_delivered INTEGER NOT NULL DEFAULT 0,
    videos_on_time INTEGER NOT NULL DEFAULT 0,
    revision_count INTEGER NOT NULL DEFAULT 0,
    quality_score REAL NOT NULL DEFAULT 0.0,
    brand_compliance INTEGER NOT NULL DEFAULT 0,
    designs_assigned INTEGER NOT NULL DEFAULT 0,
    designs_completed INTEGER NOT NULL DEFAULT 0,
    revision_rate REAL NOT NULL DEFAULT 0.0,
    scripts_assigned INTEGER NOT NULL DEFAULT 0,
    captions_assigned INTEGER NOT NULL DEFAULT 0,
    accuracy REAL NOT NULL DEFAULT 0.0,
    approval_rate REAL NOT NULL DEFAULT 0.0,
    calendar_completion INTEGER NOT NULL DEFAULT 0,
    account_health INTEGER NOT NULL DEFAULT 0,
    enquiry_response REAL NOT NULL DEFAULT 0.0,
    follow_ups_completed INTEGER NOT NULL DEFAULT 0,
    qualified_leads INTEGER NOT NULL DEFAULT 0,
    conversion_rate REAL NOT NULL DEFAULT 0.0,
    revenue REAL NOT NULL DEFAULT 0.0,
    week TEXT NOT NULL DEFAULT '',
    month TEXT NOT NULL DEFAULT '',
    computed_at TEXT NOT NULL DEFAULT (datetime('now')),
    notes TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT NOT NULL,
    client_workspace_id TEXT,
    name TEXT NOT NULL DEFAULT '',
    campaign_type TEXT NOT NULL DEFAULT 'brand',
    objective TEXT NOT NULL DEFAULT '',
    budget_plan TEXT NOT NULL DEFAULT '{}',
    start_date TEXT NOT NULL DEFAULT '',
    end_date TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'planning',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL DEFAULT 'weekly',
    report_period TEXT NOT NULL DEFAULT '',
    workspace_id TEXT NOT NULL,
    client_workspace_id TEXT,
    summary TEXT NOT NULL DEFAULT '{}',
    raw_metrics TEXT NOT NULL DEFAULT '{}',
    generated_at TEXT NOT NULL DEFAULT (datetime('now')),
    author_id INTEGER,
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_client_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id TEXT DEFAULT 'SSC',
    client_workspace_id TEXT NOT NULL,
    company_name TEXT NOT NULL DEFAULT '',
    brand_voice TEXT NOT NULL DEFAULT '',
    target_audience TEXT NOT NULL DEFAULT '',
    service_package TEXT NOT NULL DEFAULT '',
    contract_metadata TEXT NOT NULL DEFAULT '{}',
    billing_records TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(client_workspace_id),
    FOREIGN KEY (client_workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel TEXT NOT NULL DEFAULT 'internal',
    kind TEXT NOT NULL DEFAULT '',
    severity TEXT NOT NULL DEFAULT 'info',
    message TEXT NOT NULL DEFAULT '',
    payload TEXT NOT NULL DEFAULT '{}',
    read_by INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS social_agent_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_code TEXT NOT NULL DEFAULT '',
    workspace_id TEXT NOT NULL,
    client_workspace_id TEXT,
    tool_name TEXT NOT NULL DEFAULT '',
    permission_ok INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'running',
    result_summary TEXT NOT NULL DEFAULT '',
    error TEXT,
    queue_time TEXT,
    started_at TEXT,
    processing_time TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (workspace_id) REFERENCES social_workspaces(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS social_integration_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service TEXT NOT NULL DEFAULT '',
    operation TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'ok',
    detail TEXT NOT NULL DEFAULT '',
    error TEXT,
    started_at TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at TEXT
);

CREATE INDEX idx_social_accounts_workspace ON social_accounts(workspace_id);
CREATE INDEX idx_social_accounts_client ON social_accounts(client_workspace_id);
CREATE INDEX idx_social_content_workspace ON social_content_items(workspace_id);
CREATE INDEX idx_social_leads_workspace ON social_leads(workspace_id);
CREATE INDEX idx_social_video_job_workspace ON social_video_jobs(workspace_id);
CREATE INDEX idx_social_approvals_content ON social_approvals(content_id);
CREATE INDEX idx_social_publish_job_content ON social_publish_jobs(content_id);
CREATE INDEX idx_social_comments_account ON social_comments(account_id);
CREATE INDEX idx_social_agents_workspace ON social_agent_runs(workspace_id);
"""

_DEMO_BRAND = """\
{
  "business_name": "Shah Surveyors & Consultancy",
  "brand_voice": "professional and expert",
  "tone": "authoritative, educational",
  "brand_colors": {"primary":"#0B5FA5","secondary":"#128C7E","accent":"#F59E0B"},
  "brand_logo_url":"",
  "service_locations":["Singrauli","Waidhan","Ghairdabad","Khagaria","Bhagalpur","Chhotasamudra"]
}"""

_DEMO_PILLARS = [
    "Surveying education","DGPS technology","Drone survey","Topographical survey",
    "GPR underground utility survey","Industrial mapping","Site progress","Survey equipment",
    "Survey problem-solving","Project showcases","Technical explainers","Team and field operations",
    "Client education","Company capability","Industry developments","Case studies",
    "Recruitment","Festival and company announcements",
]

_DEMO_SSC_STRATEGY = {
    "business_name": "Shah Surveyors & Consultancy",
    "business_context": "Surveying, geospatial and project consultancy",
    "service_locations": ["Singrauli","Waidhan"],
    "primary_audience": [
        "Infrastructure companies","Construction contractors","Mining companies",
        "Industrial plants","EPC contractors","Solar projects","Government and PSU contractors",
        "Project consultants","Civil and survey professionals"
    ],
    "content_pillars": _DEMO_PILLARS,
    "platform_focus": {
        "instagram": {"aspect":"9:16","format":["Reel","Story"]},
        "facebook": {"aspect":"1:1","format":["Post","Video"]},
        "linkedin": {"aspect":"1:1","format":["Post","Article"]},
        "youtube": {"aspect":"16:9","format":["Shorts","Long"]},
    },
    "content_idea_templates": {
        "surveying_education": "%d illustrates %s — %s",
        "tech_insight": "Why %s matters for %s in %s",
        "case_study": "From %s to %s — a %s project",
        "equipment": "The %s — what it does and when to use it",
        "field_ops": "Day in the life: %s at %s",
        "problem_solving": "How we solved %s using %s",
        "client_education": "What %s means for your %s",
    },
}

def create_m19_tables(conn) -> None:
    """Create M19 tables idempotently and ensure column migrations."""
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='social_accounts'"
    ).fetchone()
    if not cur:
        conn.executescript(_DOMAIN_SCHEMA)
    # Ensure workspace_id exists on social_client_profiles
    try:
        conn.execute("ALTER TABLE social_client_profiles ADD COLUMN workspace_id TEXT DEFAULT 'SSC'")
    except Exception:
        pass
    conn.commit()


def seed_m19_demo(conn, workspaces) -> None:
    """Seed synthetic demo content, brand profiles and an SSC brand on the temp db."""
    ws_by_code = {w["code"]: w["id"] for w in workspaces}
    if not ws_by_code:
        return
    for code, label in [("SSC","Shah Surveyors & Consultancy")]:
        conn.execute(
            "INSERT OR IGNORE INTO social_workspaces (id,code,label,is_isolated) VALUES (?,?,?,1)",
            (code, code, label))
    # brand profiles
    for w in workspaces:
        if conn.execute(
            "SELECT 1 FROM social_brand_profiles WHERE workspace_id=?",
            (w["id"],)).fetchone():
            continue
        conn.execute(
            "INSERT INTO social_brand_profiles (workspace_id,client_workspace_id,business_name,brand_voice,brand_colors,service_locations) "
            "VALUES (?,?,?,?,?,?)",
            (w["id"], None,
             "Shah Surveyors & Consultancy",
             "professional and expert",
             json.dumps(_DEMO_BRAND, indent=2),
             json.dumps(_DEMO_PILLARS)))
    conn.commit()


def create_schema_from_db(conn) -> None:
    """Human-readable manifest of the M19 schema (used by migration tooling)."""
    rows = conn.execute(
        "SELECT name, sql FROM sqlite_master "
        "WHERE type='table' AND name LIKE 'social_%' ORDER BY name"
    ).fetchall()
    return "\n".join(str(r[1]) for r in rows)
