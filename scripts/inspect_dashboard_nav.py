with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'<nav[^>]*>.*?</nav>', text, re.DOTALL | re.IGNORECASE)
if matches:
    print("Nav element found:")
    print(matches[0][:800])
else:
    print("No <nav> tag. Searching for sidebar or menu:")
    m2 = re.findall(r'<aside[^>]*>.*?</aside>', text, re.DOTALL | re.IGNORECASE)
    if m2:
        print(m2[0][:800])
    else:
        links = re.findall(r'<a[^>]+onclick=[\'"][^\'"]*[\'"][^>]*>.*?</a>', text[:100000])
        print("Sample clickable links:", links[:10])
