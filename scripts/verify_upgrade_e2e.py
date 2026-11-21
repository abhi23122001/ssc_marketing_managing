# scripts/verify_upgrade_e2e.py
"""Verification test script for upgraded Integration Center & Creative Studio APIs."""
import json
import os
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:8899"

def req(path, method="GET", data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data is not None else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"raw": raw}
    except Exception as ex:
        return 0, {"error": str(ex)}

def run():
    print("=== TESTING UPGRADED INTEGRATION CENTER & CREATIVE STUDIO APIS ===")
    results = {}

    # 1. Login as Owner
    status, res = req("/api/auth/login", "POST", {"username": "owner", "password": "demo-owner-pass-0001"})
    token = res.get("token")
    assert status == 200 and token, f"Login failed: {status}"
    print("[PASS] Owner login successful.")

    # 2. Test Integration Center Health Monitor
    st, r = req("/api/integrations/center/health?workspace=SSC", token=token)
    assert st == 200, f"Health monitor failed: {st}"
    providers = r.get("providers", [])
    print(f"[PASS] Integration Health Monitor: {len(providers)} providers tracked. Active modules: {r.get('active_modules_count')}/{r.get('total_modules')}")
    results["integration_health"] = {"status": st, "providers_count": len(providers)}

    # 3. Test Google Sheets 12-Module Mappings
    st, r = req("/api/integrations/sheets/mappings?workspace=SSC", token=token)
    assert st == 200, f"Sheets mappings failed: {st}"
    mappings = r.get("mappings", [])
    print(f"[PASS] Google Sheets Module Mappings: {len(mappings)}/12 modules mapped.")
    assert len(mappings) >= 12, "Expected 12 core modules mapped"
    results["sheets_mappings"] = {"status": st, "modules_mapped": len(mappings)}

    # 4. Test Updating a Sheet Mapping
    st, r = req("/api/integrations/sheets/mappings?workspace=SSC", "POST", {
        "module_key": "leads",
        "spreadsheet_name": "SHAH GROUP OS — SSC Master Pipeline",
        "worksheet_tab": "CRM_Inbound_Leads",
        "sync_mode": "auto",
        "sync_enabled": True
    }, token=token)
    assert st == 200, f"Update mapping failed: {st}"
    print("[PASS] Google Sheets Mapping Update successful.")

    # 5. Test Google Drive Hierarchy & Folders
    st, r = req("/api/integrations/drive/folders?workspace=SSC", token=token)
    assert st == 200, f"Drive folders failed: {st}"
    folders = r.get("folders", [])
    print(f"[PASS] Google Drive Hierarchy: {len(folders)} folders in {r.get('root_folder')}")
    results["drive_folders"] = {"status": st, "folders_count": len(folders)}

    # 6. Test Staging a File into Google Drive Folder
    st, r = req("/api/integrations/drive/upload?workspace=SSC", "POST", {
        "filename": "DPR_Highway_Topographical_Survey.pdf",
        "module_key": "projects",
        "file_b64": "U0hBSCBHUk9VUCBBSSBPUyDigJQgVmVyaWZpZWQgU3VydmV5IFJlcG9ydA=="
    }, token=token)
    assert st == 201, f"Drive upload failed: {st}"
    print(f"[PASS] File staged in Google Drive folder: {r.get('filename')} in folder '{r.get('folder')}'")
    results["drive_upload"] = {"status": st, "file_id": r.get("file_id")}

    # 7. Test Integration Activity Logs
    st, r = req("/api/integrations/center/logs?workspace=SSC", token=token)
    assert st == 200, f"Logs failed: {st}"
    logs = r.get("logs", [])
    print(f"[PASS] Integration Activity Audit Trail: {len(logs)} activity records retrieved.")
    results["activity_logs"] = {"status": st, "count": len(logs)}

    # 8. Test Studio Project Persistence (Image Canvas)
    st, r = req("/api/studio/projects?workspace=SSC", "POST", {
        "title": "DGPS Technical Directive Carousel",
        "project_type": "image_carousel",
        "aspect_ratio": "9:16",
        "canvas_json": json.dumps([{"id": 1, "type": "text", "text": "DGPS Accuracy"}])
    }, token=token)
    assert st == 200, f"Save canvas project failed: {st}"
    proj = r.get("project", {})
    canvas_proj_id = proj.get("id")
    print(f"[PASS] Saved Canvas Project to database: ID {canvas_proj_id}")
    results["save_canvas_project"] = {"status": st, "id": canvas_proj_id}

    # 9. Test Studio Project Persistence (Video Reel)
    st, r = req("/api/studio/projects?workspace=SSC", "POST", {
        "title": "Drone LiDAR Highway Survey Reel",
        "project_type": "reel_video",
        "aspect_ratio": "9:16",
        "timeline_json": json.dumps({"duration": 6, "audio": "synth_drone", "hook": "Precision Highway Surveying"})
    }, token=token)
    assert st == 200, f"Save video project failed: {st}"
    proj = r.get("project", {})
    video_proj_id = proj.get("id")
    print(f"[PASS] Saved Video Project to database: ID {video_proj_id}")
    results["save_video_project"] = {"status": st, "id": video_proj_id}

    # 10. Test AI Image Generation Workflow
    st, r = req("/api/studio/ai-image/generate?workspace=SSC", "POST", {
        "prompt": "Survey of India DGPS base station pillar in Nagpur topography",
        "aspect_ratio": "1:1",
        "style": "surveying_dgps"
    }, token=token)
    assert st == 200, f"AI image gen failed: {st}"
    img_asset = r.get("asset", {})
    print(f"[PASS] AI Image Generation Workflow: Provider '{r.get('provider')}', File: {img_asset.get('filename')}")
    results["ai_image_gen"] = {"status": st, "provider": r.get("provider"), "filename": img_asset.get("filename")}

    # 11. Test Video Reel Rendering with Local FFmpeg
    st, r = req("/api/studio/render?workspace=SSC", "POST", {
        "project_id": video_proj_id,
        "title": "DGPS Fast Survey Reel",
        "duration_seconds": 3,
        "hook_text": "High Precision DGPS RTK",
        "body_text": "Centimeter-level accuracy for infrastructure",
        "aspect_ratio": "9:16"
    }, token=token)
    assert st == 200, f"Render reel failed: {st}"
    print(f"[PASS] Local FFmpeg Video Reel Render: Output '{r.get('video_url')}', Duration: {r.get('duration_seconds')}s")
    results["video_render"] = {"status": st, "video_url": r.get("video_url")}

    os.makedirs("AUDIT_TEST_EVIDENCE", exist_ok=True)
    with open("AUDIT_TEST_EVIDENCE/upgrade_api_verification.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\nALL UPGRADED INTEGRATION & STUDIO APIS VERIFIED 100% PASS!")

if __name__ == "__main__":
    run()
