# SHAH AI — Phase 4 Consolidated Implementation Backlog

**Project root:** C:/Users/HP/Desktop/ssc_marketing_managing
**Branch:** main | **HEAD:** a21e9f7
**Date:** 2026-11-17
**Purpose:** Single source of truth for the coordinated Phase 4 program.
No module is approved/implemented in isolation; the whole list below is one program.

---

## 1. Phase A — Audit summary (completed)

### 1.1 What exists (verified by read)
- **Runtime:** Hermes Agent pinned as Git submodule `vendor/hermes-agent`
  (`081e8d9b75b2bedae297a89232b04ef9be7b26a0`, unchanged).
- **Branding:** `config/SOUL.md` (persona), `.hermes/skills/shah-ai/SKILL.md`
  (project skill — **PROTECTED**), `brand/ssc-brand-profile.md` (**PROTECTED**).
- **Command Center:** `COMMAND-CENTER.md` + `Start-SHAI-Center.ps1` (+ `shared/scripts/{Open-Readme,Write-Draft,Summary,Calendar}.ps1`).
- **Modules 01–10:** README-only placeholders for 01–05, 08, 09, 10; functional
  console scripts for 06 (CRM-Leads.py), 07 (SEO-Keywords.py) and 11
  (Command-Center.py + Start-SHAI-Command-Center.ps1); 13 (Lead-Intelligence.py +
  Start-SHAI-Lead-Intelligence.ps1) already added in Sprint 1.
- **Shared:** `shared/templates/` (approval-form, content-template, marketing-brief,
  qa-checklist, keyword-cluster, lead-qualification, report) + `shared/scripts/`.
- **Data (non-confidential):** `data/leads.csv` (18 cols, 4 rows), `data/keywords.csv`
  (22 rows), `data/content-calendar.csv`, `data/instagram-library.csv`,
  `data/linkedin-topics.csv`, `data/status-tasks.csv`, `data/gbp-audit-checklist.csv`.
- **Docs:** `docs/{MODULES-ARCHITECTURE,CONTENT-QA-CHECKLIST,SETUP-WINDOWS,PHASE-3-CHECKPOINT,PHASE-4-SPRINT-1-REPORT}.md`.

### 1.2 Verified baseline hashes (for no-data-changed checks)
| File | MD5 / bytes |
|---|---|
| `data/leads.csv` | `5661bba39582c608fcf519d243101570` (MD5) |
| `data/keywords.csv` | `7595a7731de87f89718d8c16fd614348` (MD5) |
| `.hermes/skills/shah-ai/SKILL.md` | 7359 bytes — untouched |
| `vendor/hermes-agent` | submodule `081e8d9b75b2bedae297a89232b04ef9be7b26a0` — unchanged |
| `.github/workflows/validate.yml` / `.gitignore` | modified (preserve, do NOT commit) |

### 1.3 Identified gaps
- **M12 numbering gap** — nothing exists for module number M12.
- **M14** — Email Assistant structure exists only in the plan; OAuth/Google
  credentials are not present and are required for any Gmail access.
- No `Automation Engine`, no consolidated `Task & Follow-up`, no `Email Assistant`.

---

## 2. Consolidated implementation backlog (one program)

### 2.1 M12 — Content Calendar & Content Generation  (FILL the number gap)
**Proposed purpose:** bridge M11 (Command Center) and M13 (Lead Intelligence).
Consolidates the content-generation work currently spread across modules 02/03/04/05
into one shared calendar + generative drafting tool.

| Item | Plan |
|---|---|
| `modules/12-content-calendar-content-generation/README.md` | Purpose, workflow, approval boundary |
| `scripts/ContentCalendar.py` | `list / view / add / export / validate / integrity-check` (stdlib, read-write to a NEW calendar file; never touches shared `data/leads.csv`) |
| `scripts/ContentGenerator.py` | Pure drafting: `blog / reel / linkedin / gbp-post / outreach` using shared templates; writes drafts to `outputs/` |
| `Start-SHAI-Command-Center.ps1` | Windows launcher (dispatches subcommands) |
| Docs | `COMMAND-CENTER.md`, `MODULES-ARCHITECTURE.md`, `validate.yml` index update |

### 2.2 M14 — Email Assistant (draft-only; Gmail sync BLOCKED on OAuth)
| Item | Plan |
|---|---|
| `modules/14-email-assistant/README.md` | OAuth setup flow + strictly draft-only design |
| `scripts/EmailAssistant.py` | Classification (NTPC/Clients/Contractors/Vendors/Finance/HR/Personal/Notifications), summary, priority, follow-up recommendation, bilingual draft — NO Gmail method is wired until credentials exist |
| `Start-SHAI-Email-Assistant.ps1` | Launcher; refuses to run without a configured, out-of-repo token file |
| Tests | Unit tests for classify / priority / follow-up / bilingual draft / no-credentials refusal |

### 2.3 Consolidation tasks (no new heavy modules)
| Item | Plan |
|---|---|
| `shared/scripts/Task-Followup.ps1` | Single console view over `status-tasks.csv` AND leads follow-up-due/overdue (from CRM logic) |
| `scripts/AutomationPlanner.py` | Dry-run automation runbook: declares triggers + allowed actions, validates, produces a status report; **no network/state-changing execution** |

### 2.4 Documentation and integration
- `COMMAND-CENTER.md` — add module 12 + 14 navigation rows.
- `docs/MODULES-ARCHITECTURE.md` — add M12/M14 and the two consolidation scripts to the module map.
- `.github/workflows/validate.yml` — add modules/12-*/README.md and 14-*/README.md checks (in-place edit only; never commit).

### 2.5 Tests (all stdlib `unittest`, no pytest dependency)
- Unit: `ContentCalendar.py`, `ContentGenerator.py`, `EmailAssistant.py`, `AutomationPlanner.py`.
- Integration: M12 + M14 end-to-end with temporary data only.
- Regression: M01–M11 and M13 unchanged — re-run their existing launchers & scripts.
- Verify protected files unchanged: `data/leads.csv` MD5, `SKILL.md` bytes, submodule commit, `vendor/` tree.

---

## 3. Rollout sequence (coordinated batches — no per-module approval)

### Batch 0 — Do not touch
- `vendor/hermes-agent` (submodule, protected).
- `data/leads.csv` schema and records (MD5 must stay `5661...`).
- `config/SOUL.md`, `.hermes/skills/shah-ai/SKILL.md`, `brand/*`.
- `Start-SHAI-Center.ps1` dispatch logic is edited at the END, after all core modules exist.

### Batch 1 — M12 module (complete)
- Write M12 README + both Python scripts + PowerShell launcher.
- Verify: `py_compile`, run each subcommand with temporary data, run unit tests.

### Batch 2 — M14 module + integrations
- Write M14 README + `EmailAssistant.py` + launcher + tests.
- Write `Task-Followup.ps1` + `AutomationPlanner.py`.
- Run all unit + integration + regression tests.

### Batch 3 — Docs + security hardening
- Update `COMMAND-CENTER.md`, `MODULES-ARCHITECTURE.md`, `validate.yml` (in place).
- Run a security scan (no secrets/passwords/tokens in files; no `git add/commit/push`).
- Verify protected files unchanged (MD5 / bytes / submodule).

### Batch 4 — Final verification + backup
- Re-run full test suite, capture actual pass/fail counts.
- Verify `data/leads.csv` unchanged; backups untouched; no commits/pushes.
- Produce the consolidated completion report (this is the LAST action).

---

## 4. Rules that stay in force for the whole program
- Canonical root only: `C:/Users/HP/Desktop/ssc_marketing_managing`.
- Do NOT use the OneDrive Desktop copy.
- No external email/messages/social publishing without explicit per-action approval.
- No automatic Gmail sending.
- No destructive production operations.
- No credentials or tokens in Git; OAuth stays out of the repository.
- Never commit/push; never add optional dependencies without documenting why.
- Do NOT alter `data/leads.csv` schema.
- Protected files (`SKILL.md`, `vendor/hermes-agent`, backup dirs) remain untouched.
- Everything is draft-only until an approved `approval-form.md` record exists.

---

## 5. Numbers that must be reported at the end (actual, not predicted)
- Number of files created.
- Number of unit/integration/regression tests and PASS/FAIL counts.
- Verified MD5 of `data/leads.csv` at end (must equal `5661...`).
- Verified bytes of `SKILL.md` (7359) and submodule commit (unchanged).
- Count of tracked files before/after (must remain 11 — no commits, no new tracked files).
- Number of backups retained and untouched.

---

## 6. M12 numbering-gap conclusion (owner-checked)
The M-numbering used in Sprint 1 reports (`M11` Command Center, `M13` Lead
Intelligence, `M14` Email Assistant) does not match the module folder numbers
(`01`–`13`). The gap is **M12**, which sits between M11 (Command Center) and
M13 (Lead Intelligence). **Proposed purpose: Content Calendar & Content
Generation** — the shared calendar (`data/content-calendar.csv`) + generative
drafting across modules 02/03/04/05, consolidated into one place. This fills the
gap, does not invent a new CRM, and matches the Phase B architecture item
"Content Calendar and Content Generation".
