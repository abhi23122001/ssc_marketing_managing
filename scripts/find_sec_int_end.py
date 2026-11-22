with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'</section>\s*<!-- =========================================================\s*SETTINGS', text, re.IGNORECASE)
if m:
    line_no = text[:m.start()].count('\n') + 1
    print(f"sec-integrations closing tag found near line {line_no}")
    lines = text.splitlines()
    for j in range(max(0, line_no - 10), min(len(lines), line_no + 10)):
        print(f"  {j+1}: {lines[j]}")
else:
    # search for id="sec-settings"
    m2 = re.search(r'id="sec-settings"', text)
    if m2:
        line_no2 = text[:m2.start()].count('\n') + 1
        print(f"sec-settings found near line {line_no2}")
        lines = text.splitlines()
        for j in range(max(0, line_no2 - 12), min(len(lines), line_no2 + 4)):
            print(f"  {j+1}: {lines[j]}")
