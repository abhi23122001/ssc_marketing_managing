# Module 14 — Email Assistant

SHAH AI — Shah Surveyors & Consultancy (SSC)

## Purpose

A draft-only, read-only email assistant for SSC. It ingests an email (a `.eml`
file, a plain-text message, or the owner-pasted message), classifies it into one
of eight buckets, and produces a summary, priority, follow-up recommendations and
a **bilingual (English + Hinglish) reply draft** — all for the owner's review.

This module is deliberately conservative:

- **Draft-only by design.** No email is ever sent.
- **No automatic Gmail sending.** No state-changing email/messaging functions.
- **No external accounts, APIs or paid services are required or installed.**
- **Read-only by default.** The tool works on files you point it at, or on text
  you paste into the command.

The module is **blocked on one genuine owner authorization**: actual Gmail OAuth
read access. The owner must supply Google OAuth credentials and place a token
file OUTSIDE this repository before any Gmail sync runs. Until then, the Gmail
sync subcommand refuses to run.

## What this module produces

- Classification (NTPC, Clients, Contractors, Vendors, Finance, HR, Personal,
  Notifications).
- Email summary (bullet points).
- Priority (High / Medium / Low).
- Follow-up recommendations (no lead/recipient contact is made).
- Bilingual (English + Hinglish) reply draft.
- A clearly-documented `GmailSync` class that is disabled until OAuth is configured.

## Files

| File | Purpose |
|---|---|
| `README.md` | This file |
| `scripts/EmailAssistant.py` | Core CLI: analyze, classify, summary, priority, follow-up, bilingual, dry-run |
| `Start-SHAI-Email-Assistant.ps1` | Windows launcher |
| `docs/...` (referenced) | Referral to this module from COMMAND-CENTER.md and MODULES-ARCHITECTURE.md |

## How to use

```powershell
# from the project root
PS> .\\modules\\14-email-assistant\\Start-SHAI-Email-Assistant.ps1 --file messages\\inbox.eml
PS> .\\modules\\14-email-assistant\\Start-SHAI-Email-Assistant.ps1 classify --file messages\\inbox.eml
PS> .\\modules\\14-email-assistant\\Start-SHAI-Email-Assistant.ps1 bilingual --file messages\\inbox.eml
```

Direct Python use:

```powershell
python scripts\\14-email-assistant\\scripts\\EmailAssistant.py analyze --file messages\\inbox.eml
```

## Gmail OAuth setup (needs owner credentials — blocked until complete)

1. Create a Google Cloud project and enable the **Gmail API**.
2. Create an **OAuth 2.0 Client ID** (desktop/metadata) and download the
   `client_secret*.json`.
3. Authorise a token and save it as `token.json` at:

   ```
   %USERPROFILE%\.hermes\shah-ai\gmail\token.json
   ```

   (This file stays **outside this repository** and is never committed.)
4. The launcher will then read `read_only()` mode first — **never auto-send**.

## Approval boundary

- Everything above is a draft for the owner's review. No publishing, scheduling,
  messaging, contact, profile edits or spending happens without an explicit
  owner approval record (`shared/templates/approval-form.md`).
- `GmailSync.send_draft()` is a stub that never sends. Any actual send requires
  an explicit approval record and a configured, owner-placed token.json.
