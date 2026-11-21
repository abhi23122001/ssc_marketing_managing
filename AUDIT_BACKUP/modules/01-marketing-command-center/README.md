# Module 01 — Marketing Command Center

## Purpose

This module is the functional heart of the SHAH AI Marketing Management
System. It is the owner's and team's dashboard and navigation layer: a Windows
console launcher, a central project dashboard, and a pending-drafts, approvals,
and tasks board.

All of it is draft-only and navigation-only. It does not publish, schedule,
message, contact, or spend.

## What this module now contains

| File | Purpose |
|---|---|
| `COMMAND-CENTER.md` | Central dashboard, module navigation, pending drafts/approvals/tasks summary |
| `Start-SHAI-Center.ps1` | Windows 11 PowerShell launcher (opens `COMMAND-CENTER.md`) |
| `shared/scripts/Summary.ps1` | Console summary of open tasks and approvals |
| `data/status-tasks.csv` | Open tasks and approvals tracker |
| `shared/templates/approval-form.md` | Owner approval record for any external action |

## How it works

1. Run `.\Start-SHAI-Center.ps1`.
2. The launcher opens `COMMAND-CENTER.md` in the default viewer.
3. Read Section 5 of the dashboard (Pending drafts, approvals and tasks summary).
4. Choose a module to open its README.
5. Work in that module and keep each draft inside it.

## Draft-only workflow

1. Open the dashboard; review open tasks and approvals.
2. Choose a module and open its README.
3. Draft the requested content; keep each draft in the module folder.
4. Before any external action (publishing, scheduling, contacting, spending),
   complete `shared/templates/approval-form.md`.
5. Only then publish, schedule, message, or contact.

## Inputs

- Owner review of drafts and tasks.
- No external accounts, services, APIs, or paid services are required.

## Approval boundary

- No publishing, scheduling, messaging, contacting, account edits, or spending
  without an explicit owner approval record for that exact action.
- `shared/templates/approval-form.md` records owner, channel, date, and scope.
- No confidential, client, or customer material enters Git or public content.

## Outputs

- Opens the local dashboard and task board.
- Drafts are saved to `modules/<number>-<name>/` (or `outputs/` for final review copies).

## Quick workflow

1. Run `.\Start-SHAI-Center.ps1`.
2. Review the Command Center dashboard.
3. Pick a module and open its README.
4. Draft, run QA, and keep the approval record.
