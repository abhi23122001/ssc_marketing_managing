# scripts/inspect_marketing_ids.py
import re

text = open("foundation/dashboard/dashboard.html", encoding="utf-8").read()
m = re.search(r'<section\s+id=[\'"]sec-marketing[\'"][^>]*>(.*?)</section>', text, re.DOTALL)
if m:
    sec = m.group(1)
    ids = re.findall(r'id=[\'"]([^\'"]+)[\'"]', sec)
    print("Marketing section IDs:", ids)
