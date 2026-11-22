import re

with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

tabs = re.findall(r'data-tab=[\'"]([^\'"]+)[\'"]', text)
unique_tabs = list(dict.fromkeys(tabs))
print(f"Total unique tabs: {len(unique_tabs)}")
for t in unique_tabs:
    print(f"  - {t}")
