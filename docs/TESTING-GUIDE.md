# SHAH GROUP AI OS — Testing Guide

## 1. Run the foundation test battery

From the project root:

    python3 foundation/tests/run_foundation_tests.py

Exit code 0 = all pass; 1 = any failure. Tracebacks are captured in
`# [FAIL]` blocks inside the runner.

Prerequisites: Python 3.14 (stdlib only). No third-party packages installed or
required.

## 2. Run the API end-to-end

Start the API server:

    cd /c/Users/HP/Desktop/ssc_marketing_managing
    python3 foundation/api.py

The server listens on `127.0.0.1:8899` (configurable in `foundation/config.py`).

Then exercise the endpoints with any HTTP client (curl, httpie, python requests,
etc.):

    # login
    curl -s -X POST http://127.0.0.1:8899/api/auth/login \
      -H 'Content-Type: application/json' \
      -d '{"username":"owner","password":"demo-owner-pass-0001"}'
    # workspaces
    curl -s http://127.0.0.1:8899/api/workspaces
    # owner reads all workspaces
    curl -s http://127.0.0.1:8899/api/workspaces/SSC/resources
    curl -s http://127.0.0.1:8899/api/workspaces/INFRA/resources
    curl -s http://127.0.0.1:8899/api/workspaces/OTHER/resources
    # approval create + approve (Owner)
    curl -s -X POST http://127.0.0.1:8899/api/approvals -H 'Content-Type: application/json' \
      -H "Authorization: Bearer $TOKEN" -d '{"title":"Test","resource_key":"workspace-sites","description":"demo"}'
    # viewer cannot approve
    curl -s -X POST http://127.0.0.1:8899/api/approvals/1/transition \
      -H 'Content-Type: application/json' \
      -H "Authorization: Bearer $VIEWER_TOKEN" -d '{"status":"approved"}'
    # audit feed
    curl -s http://127.0.0.1:8899/api/audit/SSC
    # dashboard
    curl -s http://127.0.0.1:8899/

## 3. Test matrix

| Suite | Command | Exit 0 = |
|---|---|---|
| Foundation battery | `python3 foundation/tests/run_foundation_tests.py` | all pass |
| API e2e (manual) | start server + curl above | 200/401/403 as expected |
| Existing module regression | `python3 -m unittest discover -s tests -v` | non-protected modules only |

## 4. Notes on pre-existing gaps

- `tests/test_automation_planner.py` originally failed to import `shared.scripts`.
  The test import was corrected in `tests/test_automation_planner.py` (path and
  sys.path). No protected module was modified.
- The functional modules M06–M14 are not part of the foundation suite; they are
  tested separately via their own entry scripts.
