with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
items = re.findall(r'<div class="item[^"]*" data-sec="([^"]+)">([^<]+)', text)
print("Dashboard Navigation Sections (data-sec):")
for sec, label in items:
    print(f"  data-sec='{sec}': {label.strip()}")
