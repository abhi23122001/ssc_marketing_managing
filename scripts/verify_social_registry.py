import sys, os
sys.path.insert(0, os.path.abspath("."))
import json
from foundation.store import Store
from foundation.domains import social_integrations

s = Store()
accounts = social_integrations.list_social_accounts(s, 'SSC')
print(f"SSC Accounts Count: {len(accounts)}")
for a in accounts:
    print("-" * 50)
    print(f"ID: {a['id']}")
    print(f"Platform: {a['platform']}")
    print(f"Handle / Account ID: {a['platform_account_id']}")
    print(f"Display Name: {a['display_name']}")
    print(f"URL: {a['account_url']}")
    print(f"Status: {a['status']}")
    print(f"Status Reason: {a.get('status_reason')}")
    print(f"Linkage/Determination: {a.get('page_linkage_required')}, {a.get('meta_graph_api_notice')}")

# Test diagnostic status transitions
print("\n--- Testing Status Transitions ---")
test_id = accounts[0]['id']
for sc in ['set_expired', 'set_permission_missing', 'set_error', 'set_connected', 'set_not_connected', 'set_auth_required']:
    res = social_integrations.set_test_diagnostic_status(s, test_id, sc)
    acc = res.get('account', {})
    print(f"Scenario: {sc} -> Status: {acc.get('status')}")

# Reset all to default honest status
for a in social_integrations.list_social_accounts(s, 'SSC'):
    social_integrations.set_test_diagnostic_status(s, a['id'], 'set_auth_required')
print("\nAll accounts reset to honest Authorization Required.")
