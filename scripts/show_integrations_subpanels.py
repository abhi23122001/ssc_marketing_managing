with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('id="sec-integrations"')
idx2 = text.find('id="sec-settings"')
sub_text = text[idx1:idx2]

import re
subpanels = re.findall(r'<div id="(int-sub-[^"]+)"', sub_text)
print("Subpanels found:", subpanels)
for sp in subpanels:
    pos = sub_text.find(f'id="{sp}"')
    print(f"=== {sp} ===")
    print(sub_text[pos:pos+400])
