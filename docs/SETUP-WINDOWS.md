# Windows 11 setup

This guide keeps the SSC marketing configuration in this repository and uses the official Hermes Agent runtime from its upstream project.

## 1. Clone complete repository

Open **VS Code → Terminal → PowerShell** and run:

```powershell
git clone --recurse-submodules https://github.com/abhi23122001/ssc_marketing_managing.git
Set-Location .\ssc_marketing_managing
```

For an existing clone without Hermes source:

```powershell
git submodule update --init --recursive
```

Verify that `vendor/hermes-agent` contains the Hermes source files and a `LICENSE`.

## 2. Install Hermes

Read the official platform instructions first:
https://hermes-agent.nousresearch.com/docs/getting-started/installation

The upstream documentation currently lists a native Windows PowerShell installer:

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

This downloads and installs software. Run it only when you are ready to install Hermes and have reviewed the official installer instructions. This repository does not run it automatically.

## 3. Trust this project's skill

From the root of this repository:

```powershell
hermes skills trust
```

Project skills are not automatically trusted. Review the skill and brand profile before trusting this repository. Hermes documents project-local skills and trust here:
https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/

## 4. Configure a model/provider and start

Use the current official setup flow:

```powershell
hermes setup --portal
hermes
```

The setup flow requires an account/provider choice and may involve paid services or usage limits. No API key or account credentials are provided by this repository. Do not commit local Hermes configuration or secrets.

## 5. Try the skill

Examples:

- `/ssc-marketing-manager Create a 4-week LinkedIn and Instagram content calendar for survey services. Mark all evidence needed.`
- `/ssc-marketing-manager Draft a Hindi reel script explaining why a topographical survey is useful before construction.`
- `/ssc-marketing-manager Create a LinkedIn post from this approved project brief; do not add facts not in the brief.`

The skill produces drafts only. Review all public-facing material before publishing.

## 6. Update upstream Hermes

The source is pinned by a Git submodule. Review and update it deliberately:

```powershell
git submodule update --remote --merge vendor/hermes-agent
git add .gitmodules vendor/hermes-agent
git commit -m "Update Hermes Agent upstream"
git push
```

## Troubleshooting

- If `vendor/hermes-agent` is empty, run `git submodule update --init --recursive`.
- If Hermes does not load the SSC skill, confirm the current directory is the repository root and run `hermes skills trust`.
- If a command is unavailable, consult the documentation for the exact Hermes version pinned in the submodule.
- Do not paste tokens, credentials, or customer information into GitHub issues or commit them to this public repository.
