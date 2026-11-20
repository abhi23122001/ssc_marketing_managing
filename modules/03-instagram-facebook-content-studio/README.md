# Module 03 — Instagram and Facebook Content Studio

## Purpose

A content studio for SHAH AI's visual-first social content. It produces reels,
posts, carousels, and stories for Instagram and Facebook — using survey,
geospatial, and infrastructure education to explain the value of survey data
without unsupported outcome claims.

## What this module now contains

| File | Purpose |
|---|---|
| `data/instagram-library.csv` | Content asset ideas and templates |
| `data/content-calendar.csv` | Planning calendar (shared across modules) |
| `shared/templates/content-template.md` | Standard content draft template |
| `shared/scripts/Calendar.ps1` | Daily / weekly / monthly planning views |
| `data/gbp-audit-checklist.csv` | GBP & social QA reference |

## Draft output formats

### Reel / post / carousel / story template
```markdown
---
language: English
status: DRAFT
platform: Instagram Reels
audience: EPC & contractors
format: Reels
---

# Hook / headline
...

## Main message and value point
...

## Visual / shot list
- ...

## Caption
...

## Hashtags
...

## CTA
...

## Proof required
- ...

## Approval required
- Owner approval (complete `approval-form.md`).
```

## Hindi / English guidance

- Write captions in natural, professional Hinglish or English for Indian B2B readers.
- Keep hooks under 8–10 words for reels.
- Use a single clear CTA per post (request a discussion / share project requirements).
- Label AI-generated visuals as illustrative where used.

## Content QA

Before finalizing, run `shared/templates/qa-checklist.md`:
- No fabricated clients, projects, results, prices, or contact details.
- No unsupported survey-accuracy or certification claims.
- No AI visual represented as project evidence.
- Language natural and professional for Indian B2B audiences.

## Quick workflow

1. Choose a format (reel, post, carousel, story).
2. Pull the idea from `data/content-calendar.csv` or `data/instagram-library.csv`.
3. Draft the script, caption, and hashtags using the template.
4. Run the QA checklist.
5. Save as a draft; obtain approval before publishing or scheduling.
