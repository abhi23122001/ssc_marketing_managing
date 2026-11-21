# scripts/inspect_dashboard.py
import re

content = open("foundation/dashboard/dashboard.html", encoding="utf-8").read()
sections = re.findall(r'<section\s+id=[\'"](sec-[^\'"]+)[\'"]', content)
print("Sections found:", sections)

nav_items = re.findall(r'data-sec=[\'"]([^\'"]+)[\'"]', content)
print("Nav items:", set(nav_items))

scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
print(f"Total script blocks: {len(scripts)}")
