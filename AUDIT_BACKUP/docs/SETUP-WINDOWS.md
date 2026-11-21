# SHAH AI — Windows 11 setup

This guide installs the official Hermes Agent runtime and configures its user-facing identity and persistent persona as **SHAH AI**.

## 1. Clone the complete workspace

Open **VS Code → Terminal → PowerShell**:

```powershell
git clone --recurse-submodules https://github.com/abhi23122001/ssc_marketing_managing.git
Set-Location .\ssc_marketing_managing
```

For an existing clone without the source submodule:

```powershell
git submodule update --init --recursive
```

## 2. Install the runtime

Read the official instructions first:
https://hermes-agent.nousresearch.com/docs/getting-started/installation

The upstream Windows PowerShell installer currently documented by Hermes is:

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

This installs software and downloads dependencies. Run it only after reviewing the official instructions. It is not run by this repository's GitHub workflow.

## 3. Set the visible profile name to SHAH AI

After installation:

```powershell
hermes profile rename default "SHAH AI"
```

For the built-in default profile, this sets its display name. The internal profile ID remains `default` and the terminal executable remains `hermes`. Hermes documents that the display name appears in profile list/show, the `/profile` chat command, dashboard and desktop app:
https://hermes-agent.nousresearch.com/docs/user-guide/profiles/

## 4. Install the SHAH AI personality

Hermes loads its primary identity from `SOUL.md` inside its local `HERMES_HOME` (normally `$HOME\.hermes\SOUL.md`), not from the project working directory. See:
https://hermes-agent.nousresearch.com/docs/user-guide/features/personality

The template is `config/SOUL.md`. Review it before copying. The commands below back up any existing persona before replacing it:

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

If you already have a carefully customized persona, merge the SHAH AI identity manually instead of replacing it.

## 5. Trust this project's skill and configure a model

```powershell
hermes skills trust
hermes setup --portal
```

The setup flow requires a provider/model choice and may involve paid services or usage limits. No API key or account credentials are provided by this repository. Never commit local Hermes config or secrets.

## 6. Start SHAH AI

```powershell
hermes
```

The project skill is available as `/shah-ai` after the project is trusted. Examples:

- `/shah-ai Create a 4-week LinkedIn and Instagram content calendar for SSC. Mark all facts requiring evidence.`
- `/shah-ai Draft a Hindi reel script explaining the value of a topographical survey before construction.`
- `/shah-ai Create a LinkedIn post from this approved project brief; do not add facts not in the brief.`

## 7. Update the upstream engine carefully

The source is pinned by a Git submodule:

```powershell
git submodule update --remote --merge vendor/hermes-agent
git add .gitmodules vendor/hermes-agent
git commit -m "Update Hermes Agent upstream"
git push
```

Review upstream changes before updating. Keep upstream licence and branding notices intact.

## Safety and limitations

- SHAH AI drafts by default. It does not publish, schedule, contact leads, connect accounts or spend money without explicit approval.
- Do not add credentials, client drawings, survey coordinates, private reports or customer records to this public repository.
- Technical, engineering, surveying accuracy, geotechnical, drone-compliance and safety claims require qualified SSC review.
