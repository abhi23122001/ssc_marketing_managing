with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'(<section[^>]*id="sec-integrations"[^>]*>.*?</section>)', text, re.DOTALL)
if m:
    print("Found sec-integrations, length:", len(m.group(1)))
    print(m.group(1)[:1200])
else:
    print("sec-integrations not found by exact id regex.")
