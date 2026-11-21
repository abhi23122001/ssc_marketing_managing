# scripts/verify_dashboard_anchors.py
import os

path = r"C:\Users\HP\Desktop\ssc_marketing_managing\foundation\dashboard\dashboard.html"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

anchors = [
    'id="sec-marketing"',
    'id="sec-settings"',
    'function setupMarketingSubnav()',
    'async function renderSettings()',
    'id="subnav-marketing"',
    'id="users-manage"',
    'renderSocialAccounts',
]

for a in anchors:
    assert a in text, f"Missing anchor: {a}"
    print(f"Verified: {a}")

print("\nALL ANCHORS VERIFIED SUCCESSFULLY.")
