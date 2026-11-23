# -*- coding: utf-8 -*-
"""Scans entire git history across all commits for exposed credentials, private keys, or API secrets."""
import subprocess
import re
import sys

def main():
    cmd = ['git', 'log', '-p', '--all']
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors='ignore')
    except Exception as e:
        print(f"Error executing git log: {e}")
        return

    patterns = [
        (re.compile(r'AIza[0-9A-Za-z-_]{35}'), 'Google API Key'),
        (re.compile(r'ya29\.[0-9A-Za-z-_]+'), 'Google OAuth Access Token'),
        (re.compile(r'EAAB[0-9A-Za-z]+'), 'Facebook/Meta User Access Token'),
        (re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'), 'Private Key'),
        (re.compile(r'ghp_[A-Za-z0-9_]{36}'), 'GitHub Personal Access Token'),
        (re.compile(r'(?i)(?:client_secret)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']'), 'Client Secret Value'),
        (re.compile(r'(?i)(?:meta_app_secret)\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']'), 'Meta App Secret Value')
    ]

    commit_hash = "HEAD"
    findings = []
    line_count = 0
    total_commits = 0

    for line in proc.stdout:
        line_count += 1
        if line.startswith('commit '):
            commit_hash = line.split()[1]
            total_commits += 1
        if line.startswith('+') and not line.startswith('+++'):
            clean_line = line[1:].strip()
            # Ignore test files and documentation references where placeholders are mentioned
            if any(term in clean_line.lower() for term in ['<your-', 'placeholder', 'dummy', 'setup_required', 'example']):
                continue
            for regex, desc in patterns:
                m = regex.search(clean_line)
                if m:
                    findings.append((commit_hash, desc, clean_line[:120]))

    proc.wait()
    print(f"Scanned {total_commits} commits across {line_count} diff lines.")
    print(f"Total potential secret detections: {len(findings)}")
    for c_hash, desc, snippet in findings:
        print(f"  [!] Commit {c_hash[:8]}: {desc} -> {snippet}")

    if not findings:
        print("[OK] Zero real secrets detected in entire Git history.")

if __name__ == '__main__':
    main()
