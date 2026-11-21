# scripts/inspect_reel_markup.py
import re

text = open("foundation/dashboard/dashboard.html", encoding="utf-8").read()
m = re.search(r'<div id="sub-mkt-editor-reel"[^>]*>.*?</div>\s*<!--\s*Sub 1C', text, re.DOTALL)
if m:
    print("Found sub-mkt-editor-reel block (length:", len(m.group(0)), ")")
    print(m.group(0)[:600] + "...")
