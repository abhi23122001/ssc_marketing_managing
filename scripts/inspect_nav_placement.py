with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines[:160]):
    if '</nav>' in l or 'data-sec="settings"' in l:
        print(f"Line {i+1}: {l.strip()}")
