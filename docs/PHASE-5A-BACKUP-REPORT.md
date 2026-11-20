# SHAH GROUP AI OS — Phase 5A Backup Report

**Status: PASS (verified)** — definitive recovery archive `032550`

## Project lock (as at backup)

- Project root: `C:/Users/HP/Desktop/ssc_marketing_managing`
- Branch: `main`
- HEAD: `a21e9f775c4e564b4f5d73d1291598160d7e8350`
- Submodule `vendor/hermes-agent` @ `081e8d9b75b2bedae297a89232b04ef9be7b26a0`

## Definitive recovery archive

- Path: `C:\backups\ssc_marketing_managing_backup_20261118-20261118-032550`
- Archive: `ssc_marketing_managing.tar.gz` (gzip, fast compression)
- Members: 26,369
- Archive SHA-256: `6f9223b4e7e781b7257b64c6721aac808757c1387300799ccd1a6428f7e0c80c`
- Manifest: `ssc_marketing_manifest.json`
- Checksum file: `ssc_marketing_managing.sha256`
- Recovery bundles: `superproject.bundle`, `submodule.bundle`
- Recovery docs: `README.md` (project readme) and checksum files

## Archive verification (all PASS)

- GZIP archive integrity (gzip magic + tar read) — PASS
- Member count 26,369 — PASS
- Archive SHA-256 matches manifest SHA-256 — PASS
- Per-file hash verification: 0 failures across 26,369 files — PASS
- Regenerable submodule pack files excluded (internal bundle) — PASS
- CRM data isolation: `data/leads.csv` excluded — PASS
- Protected files (`.hermes/skills/shah-ai/SKILL.md`, `config/SOUL.md`,
  `brand/ssc-brand-profile.md`, `vendor/hermes-agent`) not included in the
  working-tree archive — PASS
- `superproject.bundle` — full superproject history, git bundle verify OK
- `submodule.bundle` — full submodule history (`vendor/hermes-agent`), git
  bundle verify OK

## Exclude policy applied

Inclusive of working tree + `.git/.git/modules` metadata, excluding only the
regenerable submodule object packs (internal `submodule.bundle` carries them).
No protected file, CRM record, or production data was deleted, renamed or
overwritten.

## Backups preserved (not deleted/renamed/overwritten)

- `C:\backups\ssc_marketing_managing_backup_20261118-002754`
- `C:\backups\ssc_marketing_managing_backup_20261118-20261118-012616`
- `C:\backups\ssc_marketing_managing_backup_20261118-20261118-032550` (this one)

Previous archive `002754` did NOT contain a full Git history bundle (its script
excluded `.git` entirely); therefore full Git and submodule recovery is
established only by `032550` (and the earlier `012616`).
