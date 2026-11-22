with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'<nav[^>]*id="nav"[^>]*>(.*?)</nav>', text, re.DOTALL)
if m:
    print(m.group(1))
