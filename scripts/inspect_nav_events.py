with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'#nav.*?addEventListener\(.*?\n\}', text, re.DOTALL)
if matches:
    print(matches[0][:600])
else:
    m2 = re.search(r'document\.querySelectorAll\(["\']#nav \.item["\']\).*?\n\}', text, re.DOTALL)
    if m2:
        print(m2.group(0)[:600])
    else:
        # search for dataset.sec
        m3 = re.findall(r'[^\n]*dataset\.sec[^\n]*', text)
        print("dataset.sec usages:", m3[:10])
