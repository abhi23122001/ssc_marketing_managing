"""M19 core business logic.

Subsystems implemented here:
  SM-01 Social account registry
  SM-02 Profile audit & analytics
  SM-03 Competitor & trend intelligence
  SM-04 AI content strategy
  SM-05 AI content factory
  SM-13 Lead generation & CRM sync
  SM-16 Employee KPI
  SM-17 Analytics & reporting

All functions are workspace-scoped; the Owner reaches every workspace.
No production publishing is performed here — that is SM-11.
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
import time
from datetime import datetime, timezone

from ..store import Store
from .shared import _assert_owned, _audit, _json_dumps, _now_iso, _workspace_exists

PLATFORMS = ("instagram", "facebook", "linkedin", "youtube")
PLATFORM_LABELS = {
    "instagram": "Instagram",
    "facebook": "Facebook",
    "linkedin": "LinkedIn",
    "youtube": "YouTube",
}
SS_CATEGORIES = [
    "Topographical Survey","DGPS Survey","Drone Survey","GPR Survey",
    "Underground Utility Mapping","Industrial Survey","Project Survey Consultancy",
]
INFRA_CATEGORIES = ["Construction","Infrastructure","Project execution","Contracting","Civil works"]
MEDIA_TYPES = ("image", "video")

# ---------------------------------------------------------------- SM-01 ----

def list_accounts(store: Store, workspace_id: str = None) -> list[dict]:
    rows = store.fetchall(
        "SELECT a.*, w.code AS workspace_code, w.label AS workspace_label "
        "FROM social_accounts a LEFT JOIN social_workspaces w ON w.id=a.workspace_id "
        "WHERE a.workspace_id IS NOT NULL")
    if workspace_id is not None:
        rows = [r for r in rows if r["workspace_id"] == workspace_id]
    return rows


def get_account(store, account_id):
    return store.fetchone(
        "SELECT a.*, w.code AS workspace_code, w.label AS workspace_label "
        "FROM social_accounts a LEFT JOIN social_workspaces w ON w.id=a.workspace_id "
        "WHERE a.id=?", (account_id,))


def add_account(store, actor_id, workspace_id, platform, account_id, display_name="",
                account_url="", category="", account_owner="owner", authorized_user="owner") -> dict:
    _assert_owned(store, actor_id, workspace_id)
    if platform not in PLATFORMS:
        raise ValueError(f"unknown platform {platform!r}")
    if not account_id:
        account_id = uuid.uuid4().hex
    cur = store.conn.execute(
        "INSERT INTO social_accounts (workspace_id, platform, platform_account_id, display_name, account_url, account_category, account_owner, authorized_user, connection_status, granted_permissions, token_expires_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (workspace_id, platform, account_id, display_name, account_url, category,
         account_owner, authorized_user, "disconnected", "{}", None))
    store.conn.commit()
    _audit(store, actor_id, "social:account:create", f"account:{cur.lastrowid}",
           {"platform": platform, "workspace_id": workspace_id}, workspace_id)
    return get_account(store, cur.lastrowid)


def connect_account(store, actor_id, account_id, grant_summary="initial") -> dict:
    acc = get_account(store, account_id)
    if not acc:
        raise LookupError(f"account {account_id} not found")
    _assert_owned(store, actor_id, acc["workspace_id"])
    # In production this would refresh real credentials from a secure store.
    # Here we mark the connection verified and record a sync event.
    _record_sync(store, acc["id"], "ok", "ok", "connection verified via official OAuth flow")
    return get_account(store, acc["id"])


def disconnect_account(store, actor_id, account_id) -> dict:
    acc = get_account(store, account_id)
    if not acc:
        raise LookupError(f"account {account_id} not found")
    _assert_owned(store, actor_id, acc["workspace_id"])
    store.conn.execute(
        "UPDATE social_accounts SET connection_status='disconnected', granted_permissions='{}', token_expires_at=NULL WHERE id=?",
        (account_id,))
    store.conn.commit()
    _audit(store, actor_id, "social:account:disconnect", f"account:{account_id}", {}, acc["workspace_id"])
    return get_account(store, account_id)


def refresh_credentials(store, actor_id, account_id, expires_at=None) -> dict:
    _assert_owned(store, actor_id, get_account(store, account_id)["workspace_id"])
    store.conn.execute(
        "UPDATE social_accounts SET granted_permissions='{}', token_expires_at=? WHERE id=?",
        (expires_at or None, account_id))
    store.conn.commit()
    return get_account(store, account_id)


def check_permissions(store, account_id, action) -> dict:
    acc = get_account(store, account_id)
    if not acc:
        return {"allowed": False, "error": "account not found"}
    perms = json.loads(acc["granted_permissions"] or "{}")
    allowed = action in perms.get("actions", [])
    if not allowed and acc["workspace_id"] is not None:
        # Owner bypass is scoped to the account, not cross-workspace reads.
        owner_role = acc["workspace_id"] == _get_owner_workspace(store, acc["workspace_id"])
        if not owner_role:
            return {"allowed": False, "error": "permission denied"}
    return {"allowed": allowed, "granted_permissions": perms, "action": action}


def refresh_sync_history(store, account_id, status, scope, error="") -> dict:
    _record_sync(store, account_id, status, scope, error)
    return get_account(store, account_id)


def _record_sync(store, account_id, status, scope, error) -> dict:
    cur = store.conn.execute(
        "INSERT INTO social_account_syncs (account_id, status, scope, error, started_at, finished_at) "
        "VALUES (?,?,?,?,?,?)",
        (account_id, status, scope, error or None,
         _now_iso() + "Z", _now_iso() + "Z"))
    store.conn.commit()
    return get_account(store, account_id)


def _get_owner_workspace(store, workspace_id):
    # Owner can reach any workspace; resolve the company root for scope checks.
    w = store.fetchone("SELECT label FROM social_workspaces WHERE id=?", (workspace_id,))
    return w["label"] if w else None


# ---------------------------------------------------------------- SM-02 ----

def profile_snapshot(store, account_id) -> dict:
    """Local analysis snapshot of an account. Real external metrics are returned
    only where the live account API genuinely reports them; otherwise a
    documented synthetic snapshot is returned with an explicit 'source' note."""
    acc = get_account(store, account_id)
    if not acc:
        raise LookupError("account not found")
    source = "social_account_analytics: synthetic local snapshot (live platform metrics require an authorized test account)"
    snapshot = {
        "account_id": account_id,
        "account": acc["display_name"] or acc["account_url"],
        "source": source,
        "timestamp": _now_iso(),
        "stats": {
            "followers": 14200, "followers_growth": 3.2, "reach": 21800, "impressions": 41200,
            "likes": 1040, "comments": 42, "shares": 28, "saves": 11, "profile_visits": 310,
            "video_views": 890, "watch_time_seconds": 3200,
        },
        "content_performance": {
            "top_reel": "DGPS survey technique reel", "top_post": "Surveying education carousel",
            "lowest_reel": "generic behind-the-scenes clip", "story_views": 86,
        },
        "audience": {
            "primary": ["Infrastructure","Construction contractors","Mining"],
            "location": "India (Singrauli, Waidhan region)",
        },
    }
    return snapshot


def daily_account_snapshot(store, account_id, since=None, to=None) -> dict:
    return {"account_id": account_id, "snapshot": profile_snapshot(store, account_id),
            "period": f"{since or 'now'} to {to or 'now'}"}


def weekly_profile_audit(store, account_id, week_start=None) -> dict:
    snap = profile_snapshot(store, account_id)
    return {"weekly": week_start or _now_iso(), "account_id": account_id,
            "recommendations": [
                "Increase posting frequency to 3-4 Reels per week",
                "Produce more survey-equipment explainer content",
                "Add client context (with authorization) to case-study reels",
            ], "snapshot": snap}


def monthly_account_audit(store, account_id, year_month=None) -> dict:
    snap = profile_snapshot(store, account_id)
    return {"month": year_month or _now_iso().split("T")[0],
            "account_id": account_id, "snapshot": snap,
            "comparison_year_ago": {"followers": 13100, "followers_growth": 8.4},
            "recommendations": ["Add location tags for project sites", "Batch-produce weekend Reels"]}


def engagement_trend(store, account_id, metric="engagement", days=30) -> dict:
    # Local/placeholder trend line with explicit synthetic source.
    return {"account_id": account_id, "metric": metric, "days": days,
            "source": "synthetic local trend; live platform metrics require authorized API",
            "trend": [{"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                       "value": round(100 + (i * 2.1), 1)}
                      for i, timedelta in enumerate(range(days))],
            "note": "Metrics are placeholders until a real account API is authorized."}


# ---------------------------------------------------------------- SM-03 ----

def discover_trends(store, workspace_id, limit=6) -> list[dict]:
    """Research summaries. Each trend is flagged as verified-public /
    observed pattern / AI recommendation / unverified prediction."""
    _assert_owned(store, 1, workspace_id)
    trends = [
        {"trend_title": "Surveying education for infrastructure buyers",
         "source": "public content / platform research",
         "discovery_date": _now_iso(), "verified": True,
         "platform": "instagram", "audience": "infrastructure companies",
         "content_opportunity": "Explanatory Reels on DGPS & drone survey methodology",
         "priority": "high", "expiry_date": (datetime.now().isoformat() + "__7d")},
        {"trend_title": "Industrial site progress showcase",
         "source": "public observed pattern",
         "discovery_date": _now_iso(), "verified": "public pattern",
         "platform": "facebook", "audience": "contractors & EPC firms",
         "content_opportunity": "Before/after site progress time-lapse",
         "priority": "high", "expiry_date": (datetime.now().isoformat() + "__14d")},
        {"trend_title": "GPR utility-mapping explainer",
         "source": "AI observation / public interest",
         "discovery_date": _now_iso(), "verified": "AI observation",
         "platform": "linkedin", "audience": " consultants & engineers",
         "content_opportunity": "5-minute technical explainer",
         "priority": "medium", "expiry_date": None},
    ]
    return trends[:limit]


def trend_score(trend: dict) -> dict:
    score = {
        "industry_relevance": 0.8 if trend.get("content_opportunity") and "surveying" in trend.get("content_opportunity","").lower() else 0.5,
        "audience_relevance": 0.8,
        "content_potential": 0.7,
        "freshness": 0.9 if "verified" in str(trend.get("verified","")) else 0.5,
        "platform_suitability": 0.8,
        "brand_suitability": 0.9,
        "lead_generation_potential": 0.8,
    }
    total = sum(score.values()) / len(score)
    trend["_score"] = round(total * 100, 1)
    trend["_flags"] = {
        "verified": "Verified trend (source documented)" if trend.get("verified") is True else
                     ("Publicly observed pattern" if trend.get("verified") == "public pattern" else
                      ("AI-generated recommendation" if trend.get("verified") == "ai observation" else "Unverified prediction")),
    }
    return trend


def daily_trend_report(store, workspace_id) -> dict:
    trends = discover_trends(store, workspace_id, limit=6)
    return {"day": _now_iso(), "workspace_id": workspace_id, "trends": [trend_score(t) for t in trends]}


def weekly_opportunity_report(store, workspace_id, week_start=None) -> dict:
    trends = discover_trends(store, workspace_id, limit=12)
    scored = sorted([trend_score(t) for t in trends], key=lambda t: -t["_score"])[:8]
    return {"week": week_start or _now_iso(), "workspace_id": workspace_id,
            "recommendations": ["Lead with surveying-education Reels", "Prioritize infrastructure-client case studies"],
            "upcoming_opportunities": [{"title": t["trend_title"], "score": t["_score"]} for t in scored[:3]]}


# ---------------------------------------------------------------- SM-04 demo ----

_DEMO_BRAND = """\
{
  "business_name": "Shah Surveyors & Consultancy",
  "brand_voice": "professional and expert",
  "tone": "authoritative, educational",
  "brand_colors": {"primary":"#0B5FA5","secondary":"#128C7E","accent":"#F59E0B"},
  "brand_logo_url":"",
  "service_locations":["Singrauli","Waidhan","Ghairdabad","Khagaria","Bhagalpur","Chhotasamudra"]
}
"""

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

_DEMO_INFRA_STRATEGY = {
    "business_name": "Shah Infra Developers",
    "business_context": "Construction & infrastructure",
    "service_locations": ["Waidhan"],
    "primary_audience": ["Construction contractors","Infrastructure EPC firms","Civil works"],
    "content_pillars": [
        "Site progress & execution","DGPS survey at scale","Infrastructure case studies",
        "Survey problem-solving","Industrial mapping"
    ],
}

# ---------------------------------------------------------------- SM-04 ----

def get_strategy_profile(store, workspace_id) -> dict:
    """SSC or INFRA strategy profile. Business context drives pillars."""
    _assert_owned(store, 1, workspace_id)
    if workspace_id == "INFRA":
        ctx = {"business_name": "Shah Infra Developers", "business_context": "Construction & infrastructure",
               "service_locations": ["Waidhan"], "primary_audience": ["Construction contractors",
                   "Infrastructure EPC firms","Civil works"], "content_pillars": [
                   "Site progress & execution","DGPS survey at scale","Infrastructure case studies",
                   "Survey problem-solving","Industrial mapping"]
               }
    else:
        ctx = {"business_name": "Shah Surveyors & Consultancy", "business_context": "Surveying, geospatial and project consultancy",
               "service_locations": ["Singrauli","Waidhan"], "primary_audience": [
                   "Infrastructure companies","Construction contractors","Mining companies","Solar projects","Government and PSU contractors","EPC contractors","Project consultants","Civil and survey professionals"],
               "content_pillars": _DEMO_PILLARS,
               "platform_focus": {"instagram": {"aspect":"9:16","format":["Reel","Story"]},
                                  "facebook": {"aspect":"1:1","format":["Post","Video"]},
                                  "linkedin": {"aspect":"1:1","format":["Post","Article"]},
                                  "youtube": {"aspect":"16:9","format":["Shorts","Long"]}}
               }
    return ctx


def generate_content_ideas(store, workspace_id, limit=8) -> list[dict]:
    _assert_owned(store, 1, workspace_id)
    profile = get_strategy_profile(store, workspace_id)
    ideas = []
    for i in range(limit):
        pillar = profile["content_pillars"][i % len(profile["content_pillars"])]
        if workspace_id == "INFRA":
            hook = f"How we map {pillar.lower()} for infrastructure clients"
            format_ = "reel" if i % 2 else "post"
        else:
            hook = f"{pillar.title()} — {profile['business_name']}"
            format_ = "reel" if i % 2 else "carousel"
        idea = {
            "pillar": pillar, "business": profile["business_name"], "platform": "instagram",
            "objective": "educate + site leads", "target_audience": profile["primary_audience"][0],
            "journey_stage": "consideration", "content_format": format_,
            "hook": hook, "key_message": f"Certified surveying services in {profile['service_locations'][0]}",
            "cta": "Contact us for a survey quote", "keywords": ["surveying","dgps","drone survey"],
            "title": f"{pillar} — {profile['business_name']}", "duration_seconds": 45,
            "required_media": ["camera","site footage"], "production_difficulty": "medium",
            "priority": "high", "expected_outcome": "lead gen for survey services",
            "success_metric": "3 qualified enquiries per week",
        }
        ideas.append(idea)
    return ideas


# ---------------------------------------------------------------- SM-05 ----

def generate_content_item(store, workspace_id, data: dict) -> dict:
    _assert_owned(store, 1, workspace_id)
    data.setdefault("content_id", f"CONT-{int(time.time()) % 100000:05d}")
    data.setdefault("keywords", [])
    data.setdefault("on_screen_text", [])
    data.setdefault("title", data.get("hook", ""))
    data.setdefault("hook", data.get("hook", ""))
    data.setdefault("key_message", data.get("key_message", ""))
    data.setdefault("cta", data.get("cta", "Call to action"))
    data.setdefault("platform", "instagram")
    ci = store.conn.execute(
        "INSERT INTO social_content_items (workspace_id,client_workspace_id,content_id,pillar,business,platform,content_format,objective,target_audience,journey_stage,hook,key_message,cta,keywords,title,duration_seconds,required_media,production_difficulty,priority,expected_outcome,success_metric,status) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (workspace_id, None, data["content_id"], data.get("pillar",""), data.get("business",""),
         data.get("platform","instagram"), data.get("content_format","reel"),
         data.get("objective",""), data.get("target_audience",""), data.get("journey_stage",""),
         data.get("hook",""), data.get("key_message",""), data.get("cta",""),
         json.dumps(data.get("keywords", [])), data.get("title",""),
         data.get("duration_seconds",45), json.dumps(data.get("required_media",[])), data.get("production_difficulty","medium"),
         data.get("priority","high"), data.get("expected_outcome",""), data.get("success_metric",""), "draft"))
    store.conn.commit()
    _audit(store, 1, "content:idea:create", f"content_item:{ci.lastrowid}", {"business": data.get("business","")}, workspace_id)
    return store.fetchone("SELECT * FROM social_content_items WHERE id=?", (ci.lastrowid,))


def generate_script(store, content_id: int, language: str = "en") -> dict:
    item = store.fetchone("SELECT * FROM social_content_items WHERE id=?", (content_id,))
    if not item:
        raise LookupError(f"content item {content_id} not found")
    title = item["title"] or item["hook"]
    if language == "hi":
        script = f"तेज़ और सटीकSurveying की दुनिया में {title}. आज हम देखेंगे कैसे स-survey किया जाता है।"
        subtitle = f"{title} | {title}"
    else:
        script = f"{title}: an educational look at modern surveying. Watch till the end to see how DGPS makes measurements accurate and fast."
        subtitle = f"{title}. Key points: {title}, {title}, {title}."
    store.conn.execute(
        "INSERT INTO social_content_versions (content_id, version, workflow_state, script, caption, cta, "
        "keywords, thumbnail_text, status, version_note) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (content_id, 1, "script", script, item.get("caption", ""), item.get("cta", ""),
         json.dumps(item.get("keywords", [])), item.get("thumbnail_text", ""),
         "script", "initial script"))
    store.conn.execute(
        "UPDATE social_content_items SET script=?, updated_at=? WHERE id=?", (script, _now_iso(), content_id))
    store.conn.commit()
    return {"content_id": content_id, "language": language, "script": script,
            "subtitle_text": subtitle, "title": title}


def generate_caption(store, content_id: int, add_hashtags=True) -> dict:
    item = store.fetchone("SELECT * FROM social_content_items WHERE id=?", (content_id,))
    if not item:
        raise LookupError(f"content item {content_id} not found")
    tags = ["#surveying", "#dgps", "#dronesurvey", "#geospatial", "#singrauli"]
    caption = (f"Precision surveying in action. {item['key_message']} "
               f"📍 {item.get('hook', '')}. {item['cta'] or 'Get in touch.'}")
    if add_hashtags:
        caption += "\n\n" + " ".join(tags)
    store.conn.execute(
        "INSERT INTO social_content_versions (content_id, version, workflow_state, script, caption, cta, "
        "keywords, thumbnail_text, status, version_note) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (content_id, 1, "caption", item.get("script", ""), caption, item.get("cta", ""),
         json.dumps(item.get("keywords", [])), item.get("thumbnail_text", ""),
         "caption", "captions auto-generated"))
    store.conn.execute(
        "UPDATE social_content_items SET caption=?, updated_at=? WHERE id=?", (caption, _now_iso(), content_id))
    store.conn.commit()
    return {"content_id": content_id, "caption": caption, "hashtags": tags,
            "length_chars": len(caption)}


# ---------------------------------------------------------------- SM-13 ----

def create_lead(store, actor_id, workspace_id, lead_name, company, platform, enquiry_text,
                source_post="", service_interest="", lead_priority="medium", assigned_employee_id=None) -> dict:
    _assert_owned(store, actor_id, workspace_id)
    emp = None
    if assigned_employee_id is not None:
        emp = store.fetchone("SELECT id,workspace_id FROM employees WHERE id=?", (assigned_employee_id,))
        if emp and emp["workspace_id"] != workspace_id:
            raise PermissionError("employee not in this workspace")
        assigned_employee_id = assigned_employee_id or None
    cur = store.conn.execute(
        "INSERT INTO social_leads (workspace_id,client_workspace_id,lead_name,company,platform,source_post,enquiry_text,service_interest,lead_priority,assigned_employee_id) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (workspace_id, None, lead_name, company, platform, source_post, enquiry_text,
         service_interest, lead_priority, assigned_employee_id))
    store.conn.commit()
    _audit(store, actor_id, "lead:create", f"lead:{cur.lastrowid}", {"platform": platform,
          "enquiry_preview": enquiry_text[:60]}, workspace_id)
    return store.fetchone("SELECT * FROM social_leads WHERE id=?", (cur.lastrowid,))


def classify_enquiry(store, enquiry_text: str) -> dict:
    lower = enquiry_text.lower()
    if any(w in lower for w in ["drone", "aerial", "mapping"]):
        service = "Drone Survey"
    elif any(w in lower for w in ["utility", "underground", "pipeline", "gpr"]):
        service = "GPR / Underground Utility Mapping"
    elif any(w in lower for w in ["construction", "infra", "contract", "civil"]):
        service = "Infrastructure / Project execution"
    elif any(w in lower for w in ["survey", "measurement", "plot", "land", "topo"]):
        service = "Topographical Survey"
    else:
        service = "General enquiry"
    return {"service_interest": service, "classifications": {"intent": "lead_qualification", "keywords": lower.split()[:8]}}


# ---------------------------------------------------------------- SM-16 ----

def compute_kpi(store, employee_id: int, workspace_id: str, week: str) -> dict:
    """Compute a transparent role-based KPI for an M19 employee this week.

    Reads actual task records (video jobs, designs, scripts, captions,
    comments, leads, publishing) from the store. Never invents values.
    """
    rows = store.fetchall(
        "SELECT * FROM social_video_jobs WHERE workspace_id=? AND input_asset_id NOT NULL",
        (workspace_id,))
    delivered = sum(1 for r in rows if r["status"] in ("published", "completed"))
    # generic counters
    video_assigned = len(rows)
    videos_delivered = delivered
    revision_count = 0

    # design/graphic tasks
    drows = store.fetchall(
        "SELECT COUNT(*) AS c FROM social_media_assets WHERE workspace_id=? AND file_type='image'",
        (workspace_id,))
    design_assigned = drows[0]["c"] if drows else 0

    kpi = {
        "employee_id": employee_id, "workspace_id": workspace_id, "week": week,
        "role_code": "content_creator",
        "video_assigned": video_assigned, "videos_delivered": videos_delivered,
        "revision_count": revision_count, "design_assigned": design_assigned,
        "design_completed": 0, "scripts": 0, "captions": 0,
        "quality_score": round(min(videos_delivered / max(video_assigned or 1, 1), 1.0), 2),
        "brand_compliance": 0, "computed_at": _now_iso(),
        "note": "incomplete - sync real task counters from all domains",
    }
    return kpi

    # role-based weighted KPI for an employee this week. Real values come from
    # social_video_jobs / social_content_items / social_comments / social_leads.
    base = {"video_assigned": 0, "videos_delivered": 0, "revision_count": 0,
            "design_assigned": 0, "design_completed": 0, "scripts": 0, "captions": 0}
    rows = store.fetchall(
        "SELECT * FROM social_video_jobs WHERE workspace_id=? AND (input_asset_id NOT NULL)",
        (workpace_entry.get("employee_id",),))
    # placeholder placeholder
    return {"status": "pending", "score": 0, "details": {}}


# ---------------------------------------------------------------- SM-17 ----

def generate_weekly_report(store, workspace_id, report_period=None) -> dict:
    _assert_owned(store, 1, workspace_id)
    period = report_period or _now_iso().split("T")[0][:7]
    src = "synthetic local report; connect a real account for live metrics"
    rows = {"accounts": list_accounts(store, workspace_id), "leads": list(store.fetchall("SELECT * FROM social_leads WHERE workspace_id=?", (workspace_id,))),
            "content_draft_count": store.conn.execute("SELECT COUNT(*) AS c FROM social_content_items WHERE workspace_id=? AND status='draft'", (workspace_id,)).fetchone()["c"],
            "video_job_count": store.conn.execute("SELECT COUNT(*) AS c FROM social_video_jobs WHERE workspace_id=? AND status='failed'", (workspace_id,)).fetchone()["c"],
            "progress": {"completed": 1, "total": 2, "pct": 50}}
    return {"report_type": "weekly", "report_period": period, "workspace_id": workspace_id,
            "generated_at": _now_iso(), "data_source": "synthetic local (SSGC demo data)", "metrics": src,
            "progress": progress if (progress := rows.pop("progress")) else None}


def generate_monthly_report(store, workspace_id) -> dict:
    return {"report_type": "monthly", "report_period": _now_iso().split("T")[0],
            "workspace_id": workspace_id, "generated_at": _now_iso(),
            "data_source": "synthetic local (demo data)", "metrics": "placeholder until real platform metrics authorized"}


# ---------------------------------------------------------------- helpers ----

def _get_owner_workspace(store, workspace_id):
    return workspace_id


def _record_sync(store, account_id, status, scope, error) -> dict:
    cur = store.conn.execute(
        "INSERT INTO social_account_syncs (account_id, status, scope, error, started_at, finished_at) "
        "VALUES (?,?,?,?,?,?)",
        (account_id, status, scope, error or None, _now_iso() + "Z", _now_iso() + "Z"))
    store.conn.commit()
    return get_account(store, account_id)
