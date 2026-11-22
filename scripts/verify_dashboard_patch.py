with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

assert 'id="sec-owner-setup"' in text, "Missing sec-owner-setup"
assert 'data-sec="owner-setup"' in text, "Missing nav owner-setup"
assert 'data-int-sub="gbp"' in text, "Missing subnav gbp"
assert 'id="int-sub-gbp"' in text, "Missing int-sub-gbp"
assert 'function loadOwnerSetupChecklist' in text, "Missing loadOwnerSetupChecklist"
assert 'function loadGBPStatus' in text, "Missing loadGBPStatus"

print("All HTML components and JS controllers verified in dashboard.html!")
print(f"Total file size: {len(text)} bytes")
