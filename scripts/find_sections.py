with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
for m in re.finditer(r'<section\s+id=["\']([^"\']+)["\']', text):
    line_no = text[:m.start()].count('\n') + 1
    print(f'Line {line_no}: <section id="{m.group(1)}">')

for m in re.finditer(r'</(main|div|body)>', text):
    line_no = text[:m.start()].count('\n') + 1
    if m.group(1) == 'main':
        print(f'Line {line_no}: </main>')
