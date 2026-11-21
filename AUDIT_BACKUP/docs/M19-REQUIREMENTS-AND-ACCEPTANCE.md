# M19 Requirements & Acceptance

## Objective

Define and verify the M19 social media marketing department requirements and acceptance criteria.

## Acceptance criteria (final)

A feature is complete only when its relevant acceptance test passes (MODULE status: PLANNED < DESIGNED < IMPLEMENTED < UNIT TESTED < INTEGRATION TESTED < SECURITY TESTED < LIVE VERIFIED < BLOCKED / PARTIAL / PENDING).

## Requirements checklist

| # | Requirement | Status |
|---|---|---|
| 1 | Four-platform integration architecture (Instagram/Facebook/LinkedIn/YouTube) | IMPLEMENTED (schema + mock adapters) |
| 2 | SSC pilot configuration (brand, audience, pillars) | IMPLEMENTED |
| 3 | Multi-business isolation (SSC/INFRA/CLIENT-X) | IMPLEMENTED (domain layer) |
| 4 | External client isolation (client_workspace_id) | IMPLEMENTED |
| 5 | Profile analytics | IMPLEMENTED (SM-02) |
| 6 | Trend intelligence | IMPLEMENTED (SM-03) |
| 7 | Content strategy | IMPLEMENTED (SM-04) |
| 8 | Content factory (Hindi/English) | IMPLEMENTED (SM-05) |
| 9 | Actual Reel rendering | VERIFIED (FFmpeg rc=0, 198KB output) |
| 10 | Voiceover and subtitle pipeline | IMPLEMENTED (code) — live TTS pending |
| 11 | Authorized audio handling | CODE only; manual selection step defined |
| 12 | Content calendar | IMPLEMENTED (SM-09) |
| 13 | Employee task assignment | IMPLEMENTED (SM-09) |
| 14 | Approval workflow (version-locked) | IMPLEMENTED (SM-10) |
| 15 | Approved publishing workflow | IMPLEMENTED (SM-11, mock-first) |
| 16 | CRM lead integration | IMPLEMENTED (SM-13) |
| 17 | Employee KPI | IMPLEMENTED (SM-16) |
| 18 | Weekly / monthly reports | IMPLEMENTED (SM-17) |
| 19 | Owner dashboard (SM-19 sections) | PENDING UI build |
| 20 | Agent permission enforcement | CODE draft — pending AI Brain wiring |
| 21 | Failure recovery | CODE structure defined |
| 22 | Documentation | IMPLEMENTED (17 docs + this file) |

## Live-verification requirements (pending owner authorization)

- Real Instagram/Facebook/LinkedIn/YouTube account connection.
- Real platform posting verification.
- Revenue attribution data.
- Live KPI aggregation from actual content/leads.

## Keywords

M19, social media marketing department, approval machine, version-locked publishing, mock-first platform adapters, workspace isolation, SSC pilot, client agency, AI content factory, FFmpeg Reel Studio.
