with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'</nav>', text)
if m:
    # find line number
    line_no = text[:m.start()].count('\n') + 1
    print(f"</nav> found at line {line_no}")
    lines = text.splitlines()
    for j in range(max(0, line_no - 8), min(len(lines), line_no + 4)):
        print(f"  {j+1}: {lines[j]}")
