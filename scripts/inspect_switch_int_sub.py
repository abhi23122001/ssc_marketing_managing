with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'function switchIntSub\([^\)]*\)\s*\{.*?\n\}', text, re.DOTALL)
if m:
    print(m.group(0))
else:
    print("switchIntSub function not found with exact regex.")
