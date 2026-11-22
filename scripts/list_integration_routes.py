import re

with open('foundation/api.py', 'r', encoding='utf-8') as f:
    text = f.read()

print("--- Integration Routes ---")
for m in re.finditer(r'[\'"](/api/[a-zA-Z0-9_/]+)[\'"]', text):
    route = m.group(1)
    if 'integration' in route or 'social' in route or 'sheet' in route or 'drive' in route:
        print(route)
