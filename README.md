# SHAH AI — Shah Surveyors & Consultancy

**SHAH AI** is the branded AI assistant workspace for Shah Surveyors & Consultancy (SSC), powered by the open-source [Hermes Agent](https://github.com/NousResearch/hermes-agent) runtime from Nous Research.

The assistant's user-facing identity is **SHAH AI**. Hermes remains the underlying upstream software name in source code, licence notices, package metadata and technical commands so upstream updates and attribution remain intact.

## What is included

- `vendor/hermes-agent/` — official Hermes Agent source as a pinned Git submodule.
- `.hermes/skills/shah-ai/SKILL.md` — SHAH AI's project skill for SSC research, marketing, content and business-development support.
- `config/SOUL.md` — SHAH AI's primary persona template.
- `brand/ssc-brand-profile.md` — SSC business context and claim-verification rules.
- `docs/SETUP-WINDOWS.md` — Windows installation, SHAH AI identity setup and first-run guide.
- `docs/CONTENT-QA-CHECKLIST.md` — public-content approval checklist.

## Get the full source

Clone with the submodule:

```powershell
git clone --recurse-submodules https://github.com/abhi23122001/ssc_marketing_managing.git
Set-Location .\ssc_marketing_managing
```

For an existing clone:

```powershell
git submodule update --init --recursive
```

## Install and brand the assistant on Windows 11

Read the [official Hermes installation guide](https://hermes-agent.nousresearch.com/docs/getting-started/installation). The upstream Windows installer currently documented by Hermes is:

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

After installation, run these commands from the repository root:

```powershell
hermes profile rename default "SHAH AI"
hermes skills trust
hermes setup --portal
```

The profile rename sets the visible display name of the default profile to **SHAH AI** in supported Hermes surfaces. The internal profile ID and executable command remain `default` and `hermes`; this is intentional and preserves compatibility.

Install the persistent persona template. This writes to your local Hermes home, not to GitHub. It makes a timestamped backup first if a persona already exists:

```powershell
$target = Join-Path $HOME ".hermes\SOUL.md"
New-Item -ItemType Directory -Force -Path (Split-Path $target) | Out-Null
if (Test-Path $target) {
    $backup = "$target.backup-$(Get-Date -Format yyyyMMdd-HHmmss)"
    Copy-Item $target $backup
    Write-Host "Existing persona backed up to: $backup"
}
Copy-Item .\config\SOUL.md $target -Force
```

Then start the assistant:

```powershell
hermes
```

Review the persona template and the [official SOUL.md documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/personality) before using it. Model/provider setup may involve an account, usage limits or paid services. No credentials are stored in this repository.

## What SHAH AI can help with

- SSC marketing strategy, Hindi/English content calendars and campaign planning.
- Instagram, Facebook, LinkedIn and YouTube drafts.
- Reels scripts, captions, carousels, posters and website content briefs.
- Local SEO, Google Business Profile post drafts and keyword research.
- Contractor/company research, B2B lead-list preparation and outreach drafts.
- Reporting templates and analysis of owner-provided campaign metrics.
- General research and workflow support for SSC.

The project skill is invoked as `/shah-ai` after the project is trusted and the assistant is running.

## Accuracy, privacy and approval

- SHAH AI creates drafts and recommendations by default. It does not publish, schedule, send messages, contact leads, connect accounts, change public business profiles or spend money without explicit approval for that exact action.
- Never invent clients, projects, approvals, certifications, equipment, survey accuracy, technical specifications, results, testimonials, prices or contact details.
- Do not expose confidential client material, survey drawings, coordinates, reports, credentials, cookies or personal information.
- Technical, engineering, geotechnical, survey-accuracy, safety and compliance claims require qualified SSC review.
- Use only original, licensed or permission-cleared media. Clearly identify AI-generated illustrative media.

## Updating the upstream engine

Hermes source is pinned as a submodule. Review upstream changes before updating:

```powershell
git submodule update --remote --merge vendor/hermes-agent
git add .gitmodules vendor/hermes-agent
git commit -m "Update Hermes Agent upstream"
git push
```

## Attribution and licences

SHAH AI is the SSC workspace/persona branding. Hermes Agent is developed by Nous Research and remains governed by the licence in `vendor/hermes-agent/LICENSE`. This repository does not claim ownership of upstream Hermes code, name or marks. Third-party components retain their respective licences.
