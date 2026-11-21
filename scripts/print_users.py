# scripts/print_users.py
import json
with open('AUDIT_TEST_EVIDENCE/database_audit.json') as f:
    d = json.load(f)
for u in d['users']:
    print(f"{u['id']}: {u['username']} | Role: {u['role']} | WS: {u['workspace_id']} | Active: {u['active']}")
