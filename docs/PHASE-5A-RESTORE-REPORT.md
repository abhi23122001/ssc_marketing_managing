# SHAH GROUP AI OS — Phase 5A Restore / Recovery Report

**Status: PASS (evidence-verified)** — isolated restore checked on the
definitive recovery archive `032550`

## Recovery evidence chain

Full recovery is established by **verified Git bundles + per-file hash
verification** on the defintive archive `C:\backups\ssc_marketing_managing_backup_20261118-20261118-032550`:

- `superproject.bundle` — full superproject history (branch `main`,
  HEAD `a21e9f775c4e564b4f5d73d1291598160d7e8350`).
- `submodule.bundle` — full `vendor/hermes-agent` history
  (`081e8d9b75b2bedae297a89232b04ef9be7b26a0`).
- Both bundles: `git bundle verify` OK.
- Per-file SHA-256: 0 failures across all 26,369 members.
- Working tree, index, staged changes, untracked files, and exact submodule
  checkout state are captured in the archive and verified.

## Isolated restore checks

An isolated extraction of the archive was performed and checked:

- Git metadata recovery — PASS (`git log`/history reachable from the superproject
  bundle).
- Submodule metadata recovery — PASS (submodule `.git/index/.git/packed-refs` and
  packed objects restored from `submodule.bundle`).
- Archive integrity (gzip + tar) — PASS.
- Protected files are NOT archived (exclude policy lists `.hermes`, and the
  `vendor/hermes-agent` gitlink is not tracked in the tar). The tar.gz therefore
  contains no protected file content; full Git history is carried by the
  `superproject.bundle` + `submodule.bundle`.
- Working-tree protected files present and unchanged relative to the pre-change
  git HEAD record — PASS (config/SOUL.md and brand/ssc-brand-profile.md are
  tracked, unmodified; vendor/hermes-agent worktree matches pinned commit
  081e8d9b75b2bedae297a89232b04ef9be7b26a0).
- CRM exclusion (`data/leads.csv`) — PASS (absent from archive).
- Manifest + checksum file present and matching — PASS.

## Important

Earlier v3 archives (021550/021910/022701/023412/025050) were superseded by v4
`032550` after isolated-restore discovered the v3 archive omitted the
superproject's own pack files (overly broad pack exclusion). Do not treat any
archive older than `032550` as a full Git recovery.

## Exact next action

If recovery is needed, use:

    python3 scripts/verify_backup_v4.py C:\backups\ssc_marketing_managing_backup_20261118-20261118-032550

followed by restoring from `ssc_marketing_managing.tar.gz` plus the two git
bundles and the checksum / manifest files.
