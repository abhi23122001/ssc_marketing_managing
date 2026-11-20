# M19 Agent Architecture

## Design

M19 coordinates specialist agents through the SHAH AI Brain. The agent layer is data-driven: each agent is registered with the brain, owns a tool allowlist, and enforces backend authorization at every tool call. The Marketing Director (SM-20) orchestrates the pipeline: Trend Researcher → Content Strategist → Script Writer → Video Editor → Voice/Audio → Graphic Designer → SEO Agent → Quality Agent → Calendar Planner → Approval Center → Publisher → Analytics Agent → Lead Agent → KPI Agent.

## Logical agents

| Agent | Role | Tools |
|---|---|---|
| Marketing Director | End-to-end pipeline orchestration | `m19:orchestrate`, `m19:plan` |
| Profile Auditor | Profile analytics, health | `m19:account:snapshot`, `m19:account:audit` |
| Trend Researcher | Trend discovery, scoring | `m19:trend:discover`, `m19:trend:score` |
| Competitor Analyst | Competitor research | `m19:competitor:list`, `m19:competitor:analyse` |
| Content Strategist | Content ideas, pillars | `m19:strategy:ideas`, `m19:strategy:profile` |
| Script Writer | Scripts, captions (HI/EN/Hinglish) | `m19:content:script`, `m19:content:caption` |
| Video Editor | Video render jobs | `m19:video:create`, `m19:video:render` |
| Voice & Audio Agent | Narration, subtitles, licensed audio | `m19:audio:voiceover`, `m19:audio:subtitles` |
| Graphic Designer | Brand-kit static graphics | `m19:graphic:create` |
| SEO Agent | Keyword & discoverability optimization | `m19:seo:optimize` |
| Calendar Planner | Content calendar / task assignment | `m19:calendar:create`, `m19:task:create` |
| Publisher | Publish only after approval | `m19:publish:enqueue` |
| Community Manager | Comment/message drafting (draft only) | `m19:community:draft` |
| Lead Generation Agent | Enquiry classification, CRM sync | `m19:lead:classify`, `m19:lead:create` |
| Analytics Agent | Metrics, reporting | `m19:report:weekly`, `m19:report:monthly` |
| KPI Agent | Employee scorecards | `m19:kpi:compute` |
| Client Account Manager | Client workspaces, approvals | `m19:client:list`, `m19:client:approve` |
| Campaign Analyst | Performance analysis | `m19:campaign:analyse` |
| Quality Agent | Accuracy, branding, media checks | `m19:quality:check` |

## Agent workflow contract

1. All agent tools are permission-checked by the backend (RBAC + workspace isolation).
2. Agents execute read/write flows through the domain layer — never bypass authorization.
3. External actions (publish, send message, spend money) are blocked by the approval machine, regardless of agent.
4. Audit trail records every agent tool call (actor_id, agent code, tool, permission_ok, status, result).

## Status

- Architecture and agent definitions: IMPLEMENTED in docs + code.
- Brain agent registry + tool wiring: PENDING (AI Brain allowlist extension + test `ai:brain:query`).
- Live agent end-to-end: BLOCKED until owner authorizes a pilot account.

## Platform mapping (SM-01→SM-20)

| System | Code path |
|---|---|
| SM-01 accounts | `m19_core.add_account` |
| SM-02/SM-03 analytics | `m19_core.profile_snapshot`, `m19_core.daily_trend_report` |
| SM-04/SM-05 strategy | `m19_core.generate_content_ideas`, `m19_core.generate_content_item`, `generate_script`, `generate_caption` |
| SM-06/SM-07/SM-08 media | `m19_media` (FFmpeg, voiceover, graphics) |
| SM-09/SM-10/SM-11 workflow | `m19_workflow` (calendar, approval, publish queue) |
| SM-13 leads | `m19_core.create_lead`, `classify_enquiry` |
| SM-16 KPI | `m19_core.compute_kpi` |
| SM-17 reporting | `m19_core.generate_weekly_report`, `generate_monthly_report` |
