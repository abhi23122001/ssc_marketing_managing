# SHAH Group AI OS — Known Issues & Defect Tracking

## 1. Resolved Issues (Verified Clean)

### Issue #1: Deactivated User Session & Login Bypass (Module 1)
- **Status**: RESOLVED & TESTED PASS
- **Location**: `foundation/store.py` (`authenticate()`, `decode_session()`, `deactivate_user()`)
- **Fix**: Added `u.active = 1` checks to `Store.authenticate` and `Store.decode_session`. Added session deletion on deactivation (`DELETE FROM sessions WHERE user_id=?`).
- **Evidence**: `tests/test_module1_hardening.py` checks 8, 9, 10 pass.

### Issue #2: RESTful User Update Path Parsing Error (Module 1 / Dashboard)
- **Status**: RESOLVED & TESTED PASS
- **Location**: `foundation/api.py` (`do_PUT`)
- **Fix**: Replaced fragile `path.split("/")[-2]` with robust URL token decomposition supporting both `PUT /api/users/{id}` and `PUT /api/users/{id}/edit`.
- **Evidence**: `tmp_full_api_test.py` and `test_module1_hardening.py` pass.

### Issue #3: Frontend Selector Null Dereference in Dashboard
- **Status**: RESOLVED & TESTED PASS
- **Location**: `foundation/dashboard/dashboard.html` (`$` selector definition)
- **Fix**: Updated `const $ = sel => typeof sel === "string" ? (sel.startsWith("#") ? document.getElementById(sel.slice(1)) : (sel.startsWith(".") || sel.includes(" ")) ? document.querySelector(sel) : document.getElementById(sel)) : sel;`.
- **Evidence**: Live browser CDP automation verified 0 console errors across all 9 dashboard tabs.

### Issue #4: Overview Pending Approvals Type Mismatch
- **Status**: RESOLVED & TESTED PASS
- **Location**: `foundation/dashboard/dashboard.html` (`renderOverview`)
- **Fix**: Added `Array.isArray(o.pending_approvals)` check so numeric counts do not invoke `.map()`.
- **Evidence**: Live browser CDP console error count dropped from 8 to 0.

### Issue #5: Stale Background Server Process & Port 8899 Contention
- **Status**: RESOLVED & TESTED PASS
- **Location**: Windows OS Process Table
- **Fix**: Terminated orphaned server PID 32456 holding SQLite database lock. Standardized on a single verified daemon on port 8899.

---

## 2. Documented Architectural Notices
1. **Demo Passwords**: Demo credentials (`demo-*-pass-0001`) are local-development placeholders only; must be rotated prior to public exposure.
2. **Social Media External Publishing**: Instagram, Facebook, LinkedIn, YouTube publishing endpoints operate in mock-first / staged approval mode until live platform OAuth credentials are provided by the business owner.
