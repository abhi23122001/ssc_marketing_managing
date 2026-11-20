# SHAH Group AI OS — Backup and Recovery Log

## 1. Backup Strategy Overview
- **Storage Target**: Local disk under `backups/antigravity_YYYY-MM-DD/` and validation archives.
- **SQLite Engine**: Online backup API (`sqlite3.backup()`) to guarantee transaction consistency in WAL mode.
- **Scope**: Source code, migrations, schemas, documentation, tests, static templates, active databases, CSV assets.
- **Verification**: SHA-256 manifest verification + isolated out-of-place restore check to `C:\temp\antigravity_restore_test_*`.

---

## 2. Backup Registry

| Date (UTC) | Backup Name | Size / Files | Target Path | Integrity Status | Restore Verified | Git Commit | Notes |
|------------|-------------|--------------|-------------|------------------|------------------|------------|-------|
| 2026-11-20 | `antigravity_2026-11-20_final` | 199 files | `backups/antigravity_2026-11-20_final` | VERIFIED (0 errors) | PASS (54 tables, 31 users, 21 leads, 23 sites, 11 clients, 13 employees, 13 leaves, 18 attendance, 12 agents, 5 payroll runs, 51 payslips) | PENDING | Final development milestone backup with complete Payroll calculation/run/approval, Payslips, CRM follow-up scheduling, CSV exports, brute-force rate-limiting, password complexity, AI Brain tool execution, and 293/293 test suite pass |
| 2026-11-20 | `antigravity_2026-11-20_phase3` | 197 files | `backups/antigravity_2026-11-20_phase3` | VERIFIED (0 errors) | PASS (54 tables, 27 users, 19 leads, 15 sites, 7 clients, 5 employees, 5 leaves, 10 attendance, 12 agents) | `a21e9f7` | Phase 3 milestone backup with full HRM module (employees, attendance, leaves with approval routing), all 12 specialist AI agents seeded, new documentation suite, and 254/254 test suite pass |
| 2026-11-20 | `antigravity_2026-11-20_phase2` | 189 files | `backups/antigravity_2026-11-20_phase2` | VERIFIED (0 errors) | PASS (54 tables, 24 users, 17 leads, 10 sites, 3 clients) | `a21e9f7` | Phase 2 milestone backup with complete CRM leads sync, lead conversion, survey sites, finance expenses & vendors, AI action gating, and dashboard enhancements |
| 2026-11-20 | `antigravity_2026-11-20_post_hardening` | 185 files | `backups/antigravity_2026-11-20_post_hardening` | VERIFIED (0 errors) | PASS (54 tables, 16 users) | `a21e9f7` | Post-hardening backup with Module 1 & dashboard fixes and browser test suite |
| 2026-11-20 | `antigravity_2026-11-20_pre_dev` | 167 files | `backups/antigravity_2026-11-20_pre_dev` | VERIFIED (0 errors) | PASS (54 tables, 11 users) | `a21e9f7` | Pre-development baseline backup before any Antigravity modifications |
| 2026-11-20 | `demo_ready_20261120_011434` | Directory | `backups/demo_ready_20261120_011434` | Historical | N/A | `a21e9f7` | Prior Hermes checkpoint |
| 2026-11-20 | `hermes_overnight_20261120` | Directory | `backups/hermes_overnight_20261120` | Historical | N/A | `a21e9f7` | Prior Hermes overnight snapshot |

---

## 3. Restore Verification Protocol
1. Unpack or copy files from the backup directory into an isolated temporary directory (e.g., `C:\temp\restore_test_isolated`).
2. Verify all file SHA-256 checksums match `backup_manifest.json`.
3. Open `data/sgcc_foundation.sqlite` in the restored directory with SQLite3.
4. Verify table count, user count, and run `PRAGMA integrity_check`.
5. Remove temporary restore test directory upon verification.
6. **NEVER restore directly over the live production database.**
