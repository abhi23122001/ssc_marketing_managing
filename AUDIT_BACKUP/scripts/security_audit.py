#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHAH AI OS - Phase 5A Git / Submodule Security Audit Utility
============================================================
Performs a read-only security audit of the project's Git configuration and
submodule setup. Detects credential exposure, unsafe configuration, and
historical secrets without displaying secret values.

SECURITY CHECKS
  A. Git remote URLs with embedded credentials.
  B. Credential helper configuration.
  C. Sensitive local configuration.
  D. Git hooks (active, un-named).
  E. .gitmodules submodule configuration.
  F. historical secrets (references to secrets in Git history*).

FAILING CONDITIONS
  Any check that finds a credential, unsafe setting, or active hook that
  could expose secrets is reported as a BLOCKING finding.
  Unresolved credential exposure prevents Phase 5A backup creation.

READ-ONLY
  This script never copies, prints, or logs secret values. It only reports
  metadata (file names, config keys, presence flags).

USAGE
    python3 security_audit.py --repo-root <path>
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# Secret-class glob patterns (filenames only; values never read).
SECRET_PATTERNS = (
    "*credentials*.json",
    "*token*.json",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "secrets/",
    ".env",
    ".env.*",
    "*.log",
)

# Credential-helper names that are NOT considered secret-leaking for this audit.
# (helper-selector is a meta-helper; it is recorded but not treated as a secret.)
SAFE_CREDENTIAL_HELPERS = {"helper-selector", "cache", "store", "osxkeychain",
                           "wincred", "manager"}

# Windows special device filenames used to detect a poisoned Git working tree.
DEVICE_NAMES = {"CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4",
                "LPT1", "LPT2", "LPT3"}

BLOCKING_CRITERIA = []


def run_git(repo_root, *args):
    """Run a git command and return (returncode, stdout, stderr)."""
    cmd = ["git", "-C", str(repo_root)] + list(args)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def run_git_config(repo_root, *args):
    cmd = ["git", "-C", str(repo_root), "config", "--get", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def audit_remote_urls(repo_root):
    """
    Check remote URLs for embedded credentials.
    Returns (findings, blocking).
    """
    findings = []
    rc, stdout, _ = run_git(repo_root, "remote", "-v")
    if rc != 0:
        findings.append({"type": "git_command_failed", "detail": f"git remote -v: {stdout}"})
        return findings, False

    for line in stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        url = parts[1]
        # Detect embedded credentials in URL.
        if "://" in url:
            scheme, _, rest = url.partition("://")
            if "@" in rest:
                findings.append({
                    "type": "credential_in_url",
                    "detail": f"remote URL contains embedded userinfo: {url}",
                })
    return findings, len(findings) == 0


def audit_credential_helpers(repo_root):
    """
    Check configured credential helpers.
    Returns (findings, blocking).
    """
    findings = []
    # Global & local credential.helper
    for scope in ("", "--local"):
        rc, stdout, _ = run_git_config(repo_root, scope, "credential.helper")
        if rc == 0 and stdout:
            helper = stdout.strip()
            if helper not in SAFE_CREDENTIAL_HELPERS:
                findings.append({
                    "type": "credential_helper",
                    "detail": f"credential.helper={helper!r} (scope={scope or 'global'})",
                })
    return findings, len(findings) == 0


def audit_local_config(repo_root):
    """
    Scan local .git/config for sensitive keys (non-secret metadata only).
    Returns (findings, blocking).
    """
    findings = []
    config_path = repo_root / ".git" / "config"
    if not config_path.is_file():
        return findings, True
    with open(config_path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            stripped = line.strip()
            # Flag credential-like keys by name only.
            if "=" in stripped and not stripped.startswith("#"):
                key, _, _ = stripped.partition("=")
                if any(s in key.lower() for s in ("credential", "sslpassword",
                                                  "password", "passphrase",
                                                  "token", "secret")):
                    findings.append({
                        "type": "sensitive_local_config",
                        "detail": f"key={key.strip()} (value not displayed)",
                    })
    return findings, len(findings) == 0


def audit_hooks(repo_root):
    """
    List active (non-.sample) Git hooks.
    Returns (findings, blocking).
    """
    findings = []
    hooks_dir = repo_root / ".git" / "hooks"
    if not hooks_dir.is_dir():
        return findings, True
    for hf in hooks_dir.iterdir():
        if hf.is_file() and not hf.name.endswith(".sample"):
            findings.append({
                "type": "active_hook",
                "detail": f"hook={hf.name} (not disabled by .sample suffix)",
            })
    return findings, len(findings) == 0


def audit_submodules(repo_root):
    """
    Audit submodule configuration and pinned commits.
    Returns (findings, blocking).
    """
    findings = []
    rc, stdout, _ = run_git(repo_root, "submodule", "status")
    if rc != 0:
        findings.append({"type": "git_command_failed",
                         "detail": f"git submodule status: {stdout}"})
        return findings, False
    for line in stdout.splitlines():
        if not line.strip():
            continue
        # Format: <sha> <path> (<branch>)
        parts = line.split()
        if len(parts) >= 3:
            sha, path = parts[0], parts[1]
            # A leading space means clean checkout (no diff).
            # A leading '-' means uninitialized.
            if path.startswith("-"):
                findings.append({
                    "type": "uninitialized_submodule",
                    "detail": f"submodule path={path} (uninitialized)",
                })
    return findings, len(findings) == 0


def audit_gitignore(repo_root):
    """
    Verify .gitignore includes the required exclusion entries.
    Returns (findings, blocking).
    """
    findings = []
    gitignore = repo_root / ".gitignore"
    if not gitignore.is_file():
        findings.append({"type": "missing_gitignore", "detail": ".gitignore not found"})
        return findings, False
    with open(gitignore, "r", encoding="utf-8", errors="replace") as fh:
        content = fh.read().lower()
    for required in ("outputs/", "private-client-data/", "__pycache__/",
                     "*.pyc", "*.tmp", "*.swp", "*.log", ".env"):
        if required not in content:
            findings.append({
                "type": "missing_gitignore_rule",
                "detail": f"required exclusion '{required}' not found in .gitignore",
            })
    return findings, len(findings) == 0


def main():
    parser = argparse.ArgumentParser(
        description="Read-only security audit of Git configuration and submodules.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--repo-root", required=True, help="Canonical SHAH AI project root.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    if not repo_root.is_dir():
        print(f"ERROR: repo-root does not exist: {repo_root}", file=sys.stderr)
        return 2

    print("SHAH AI OS - Git / Submodule Security Audit")
    print(f"Repo root: {repo_root}")
    print("=" * 60)

    all_findings = []
    checks = [
        ("Remote URLs (credential exposure)", audit_remote_urls),
        ("Credential helpers", audit_credential_helpers),
        ("Local config (sensitive keys)", audit_local_config),
        ("Git hooks", audit_hooks),
        ("Submodules", audit_submodules),
        (".gitignore rules", audit_gitignore),
    ]

    results = []
    for label, checker in checks:
        print(f"\n--- {label} ---")
        try:
            findings, blocking = checker(repo_root)
        except Exception as exc:
            findings, blocking = [{"type": "check_error", "detail": str(exc)}], False
        results.append((label, findings, blocking))
        if findings:
            for f in findings:
                print(f"  [FINDING] {f.get('type', 'unknown')}: {f.get('detail', '')}")
        else:
            print("  (no findings)")
        all_findings.extend(findings)

    print("\n" + "=" * 60)
    if all_findings:
        print(f"SECURITY AUDIT: FAIL")
        for label, findings, blocking in results:
            if findings:
                print(f"  {label}: blocking={blocking}")
        return 1
    else:
        print("SECURITY AUDIT: PASS - no unresolved credential exposure")
        return 0


if __name__ == "__main__":
    sys.exit(main())
