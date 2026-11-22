with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'data-sec.*?\{.*?\n\}', text, re.DOTALL)
if m:
    print(m.group(0)[:500])
else:
    # search for switchSection or similar
    fn = re.findall(r'function (switch[a-zA-Z0-9_]*|show[a-zA-Z0-9_]*|nav[a-zA-Z0-9_]*)\(', text)
    print("Related navigation functions:", fn[:10])
