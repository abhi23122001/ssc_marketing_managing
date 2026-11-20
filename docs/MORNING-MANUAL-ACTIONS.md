# MORNING MANUAL ACTIONS

Actions that genuinely require owner authorization. Do not perform without explicit approval.

---

## 1. Social Platform Account Connections (Required for Live Publishing)

| Platform | Action | Requirement |
|----------|--------|-------------|
| Instagram | Connect Instagram Business account | Owner: Login to Instagram, authorize via OAuth, confirm browser popup |
| Facebook | Connect Facebook Page | Owner: Admin access to Facebook Page, authorize via OAuth |
| LinkedIn | Connect LinkedIn Page | Owner: Company Page admin, authorize via OAuth |
| YouTube | Connect YouTube Channel | Owner: Brand Account owner, authorize via OAuth |
| Twitter/X | Connect account | Owner: X login, authorize via OAuth |

**Risk:** Attempting connection without owner authorization only creates mock connections. Real publishing blocked until owner approves.

---

## 2. Sample Footage Approval (Reel Studio)

| Item | Description | Action |
|------|-------------|--------|
| Sample footage | 1–3 short clips (10–30s each) from authorized projects | Owner: Provide source files for technical pipeline validation |
| Welcome/reel b-roll | Stock footage license confirmation | Owner: Confirm license coverage and usage rights |
| Duration limit | Max 60s per production by default | Owner: Confirm if 5-min productions are needed |

---

## 3. Configuration

| Setting | Default | Action |
|---------|---------|--------|
| `foundation/config.json` | None (default applied) | Owner: Review and populate `config.json` with workspace names, AI model preferences |
| Demo password for `owner` | Hash stored only | Owner: Reset to non-default after first login |
| App URL | `http://localhost:8899` | Owner: Update for deployment |

---

## 4. Permissions & Roles

| Role | Permissions | Review |
|------|-------------|--------|
| Owner | All workspaces, all tools | Verify all expected permissions granted |
| Manager | Own workspace, network tools | Confirm tech manager role included |
| Project Manager | Own workspace, SSC/INFRA views | Confirm access levels |
| Finance Manager | Expense, payroll, profit/loss | Verify finance toolchain access |
| HR Manager | Personnel data in own workspace | Confirm employee data visibility |
| Viewer | Read-only for own workspace | Add as default for clients/vendors |

---

## 5. AI Model / Provider Configuration

| Provider | Status | Action |
|----------|--------|--------|
| Local LLM (Ollama) | Not configured | Owner: Install Ollama, download a 7B model, update `config.json` `model` setting |
| Provider fallback | None configured | Owner: Choose primary + fallback provider |
| API key storage | None in repo | Owner: Add keys via environment variables or `config.json` (keep out of Git) |

---

## 6. External Integrations (require owner authorization)

| Integration | Requirement |
|-------------|-------------|
| Email (SMTP) | Owner: Provide SMTP server details, or set up local mail server |
| SMS | Owner: Choose provider (Twilio trial, local gateway) |
| Voice Voiceover | Owner: Select TTS (Piper local TTS recommended, or external voiceover) |
| Billing / Payments | Owner: Set up electronic invoicing, GST COMP 1, or contact ERP |

---

## 7. Data Population (Synthetic)

| Dataset | Current State | Action Needed |
|---------|---------------|---------------|
| Employees | Demo data seeded | Owner: Add real employees, roles, salaries |
| Attendance records | Synthetic demo | Owner: Enter real data |
| Expense claims | Synthetic demo | Owner: Enter real expenses, approve |
| Payroll | Demo data | Owner: Verify calculations, finalize |
| Leads | 15 sample leads | Owner: Add real CRM pipeline data |

---

## 8. Dashboard Features

| Feature | Status | Action |
|---------|--------|--------|
| AI Brain chat | Working | Owner: Set AI model provider |
| Reel Studio preview | Working | Owner: Provide sample footage |
| Content calendar | Working | Owner: Populate content strategy |
| Social media queue | Working | Owner: Connect platforms to publish |
| CRM pipeline | Working | Owner: Add leads |
| Approvals | Working | Owner: Approve pending items |
| Reports | Working | Owner: Validate numbers against real data |

---

## 9. Legal & Compliance

| Item | Action |
|------|--------|
| GST / Tax | Owner: Configure invoicing, GST returns, TDS |
| Labour law | Owner: Configure payslips, attendance reports |
| Contracts | Owner: Review and sign proposals |
| Data privacy | Owner: Confirm DPDP compliance and data retention |
| Media rights | Owner: Confirm footage licensing for public posts |

---

## 10. Pre-Launch Checklist

- [ ] Review `docs/NEXT-STEPS.md` for remaining tasks
- [ ] Verify workspace switching in dashboard
- [ ] Test login, logout, and role permissions
- [ ] Check `docs/TEST-RESULTS.md` (89/89)
- [ ] Review `docs/KNOWN-ISSUES.md` (2 known issues)
- [ ] Confirm all media exports produce valid files
- [ ] Validate integration tests pass in CI
- [ ] Backup production data before first deployment

---

*Document prepared for owner review. No external account changes made without owner authorization.*
