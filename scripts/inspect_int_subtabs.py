with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
subnav = re.findall(r'data-int-sub="([^"]+)"[^>]*>([^<]+)', text)
print("Integration Subtabs:")
for k, label in subnav:
    print(f"  {k}: {label.strip()}")
