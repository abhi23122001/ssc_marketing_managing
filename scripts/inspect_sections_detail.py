# scripts/inspect_sections_detail.py
import re

content = open("foundation/dashboard/dashboard.html", encoding="utf-8").read()

for sec in ['sec-overview', 'sec-workspaces', 'sec-projects', 'sec-finance', 'sec-employees', 'sec-marketing', 'sec-crm', 'sec-ai', 'sec-approvals', 'sec-settings']:
    m = re.search(r'<section\s+id=[\'"]' + sec + r'[\'"][^>]*>(.*?)</section>', content, re.DOTALL)
    if m:
        sec_content = m.group(1)
        subtabs = re.findall(r'data-sub=[\'"]([^\'"]+)[\'"]', sec_content)
        buttons = re.findall(r'<button[^>]*onclick=[\'"]([^\'"]+)[\'"]', sec_content)
        h2s = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', sec_content)
        print(f"\n=== {sec} (length: {len(sec_content)} bytes) ===")
        print("  Headings:", [re.sub(r'<[^>]+>', '', h).strip() for h in h2s[:5]])
        if subtabs:
            print("  Subtabs (data-sub):", set(subtabs))
        if buttons:
            print("  Sample button onclicks:", buttons[:5])
