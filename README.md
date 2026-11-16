# SSC Marketing Manager — powered by Hermes Agent

A Shah Surveyors & Consultancy (SSC) marketing workspace built on the open-source Hermes Agent project by Nous Research.

## Repository layout

- `vendor/hermes-agent/` — Git submodule pointing to the official upstream source. The source is pinned to a specific upstream commit so a checkout is reproducible.
- `.hermes/skills/ssc-marketing-manager/SKILL.md` — project-local Hermes skill for SSC marketing work.
- `brand/ssc-brand-profile.md` — known business context and claim-verification rules.
- `docs/SETUP-WINDOWS.md` — Windows installation and first-run guide.

Hermes source is maintained by [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent). This repository does not copy, relicense, or claim ownership of upstream code; the submodule retains its upstream commit and licence.

## Get the complete source checkout

Clone this repository with its submodule:

```powershell
git clone --recurse-submodules https://github.com/abhi23122001/ssc_marketing_managing.git
cd ssc_marketing_managing
```

If you already cloned without submodules:

```powershell
git submodule update --init --recursive
```

The `vendor/hermes-agent` folder is the complete Hermes source checkout, pinned to the version recorded in this repository.

## Install Hermes on Windows 11

The upstream Hermes documentation currently provides a native Windows PowerShell installer and a Desktop installer. Review the official instructions first:

- [Official Hermes documentation](https://hermes-agent.nousresearch.com/docs)
- [Official Windows installation instructions](https://hermes-agent.nousresearch.com/docs/getting-started/installation)

For the CLI installer, the upstream documentation currently documents:

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

Run that only after reviewing the official installation notes. It installs software and downloads dependencies; it is not run by this repository's GitHub workflow.

After installation, open PowerShell in this repository and trust its project skills:

```powershell
hermes skills trust
hermes setup
hermes
```

For model/provider setup, use Hermes' interactive setup and its current official documentation. Do not paste API keys into this repository or commit local Hermes config files.

## Use the SSC marketing skill

Start Hermes from the root of this checkout after trusting the project. The project skill is then available in the session. Ask for tasks such as:

- Hindi/English content calendars, campaign plans and content pillars.
- Reels, captions, carousels, scripts, YouTube descriptions and hashtags.
- Local SEO drafts, Google Business Profile post drafts and website service-page drafts.
- Lead-response templates and monthly marketing reports.

The skill creates drafts and recommendations. It does not publish, schedule, message leads, connect social accounts, spend money, or disclose customer/client information without separate explicit approval and a configured integration.

## Accuracy and safety

- Do not invent clients, projects, locations, approvals, certifications, qualifications, equipment, survey specifications, accuracy figures, results, testimonials, prices, or contact details.
- Treat technical and commercial claims as unverified until SSC supplies evidence and approves them.
- Do not place confidential survey data, client drawings, coordinates, phone numbers, credentials, cookies, or personal information in public content or Git.
- Require a qualified SSC reviewer for engineering, geotechnical, survey-accuracy, safety, and compliance statements.
- Use only original, licensed, or permission-cleared media. Keep source and licence details for assets.
- All external-facing content remains a draft until a human approves it.

## Updating Hermes source

The submodule is intentionally pinned. Review upstream changes before updating it:

```powershell
git submodule update --remote --merge vendor/hermes-agent
git add .gitmodules vendor/hermes-agent
git commit -m "Update Hermes Agent upstream"
git push
```

## Licence

Hermes Agent remains under the licence provided by Nous Research in the submodule (see `vendor/hermes-agent/LICENSE`). SSC-specific instructions and brand notes in this repository are provided for this project. Third-party components keep their own licences.
