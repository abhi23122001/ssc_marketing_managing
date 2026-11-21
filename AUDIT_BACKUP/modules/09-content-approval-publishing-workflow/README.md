# Module 09 — Content Approval and Publishing Workflow

## Purpose

The approval and publishing gateway for the SHAH AI Marketing Management
System. It ensures that nothing is published, scheduled, messaged, or
contacted without an explicit, recorded owner approval for that exact
action.

## What this module contains

- Approval record form (owner, channel, date, reason).
- Draft-to-publication state machine (draft -> QA -> review -> approval -> publish).
- Publishing block: content that is not approved cannot leave the draft
  folder.
- QA checklist reference (see `docs/CONTENT-QA-CHECKLIST.md`).

## Workflow

1. Draft the content in the relevant module.
2. Run the QA checklist.
3. Flag technical claims for qualified SSC review.
4. Present the content to the owner for approval.
5. Record the approval (who, which channel, date, reason).
6. Only after approval is saved to `outputs/` or `generated/`.

## Approval record fields

- Owner name
- Channel (Instagram, Facebook, LinkedIn, YouTube, GBP, email, etc.)
- Date
- Content title / reference
- Approval status
- Comments / conditions

## Approval boundary

- Publishing, scheduling, messaging, contacting, profile edits, ad spend,
  and external account actions require the approval record above.
- This module performs no external action itself.

## Quick workflow

1. Produce a draft.
2. QA the draft.
3. Get owner approval for the exact action.
4. Record approval.
5. Publish only when the record exists.
