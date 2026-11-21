# scripts/inspect_canvas_html.py
import re

text = open("foundation/dashboard/dashboard.html", encoding="utf-8").read()

for panel_id in ['sub-editor-canvas', 'sub-editor-reel', 'sub-ai-image', 'sub-media']:
    m = re.search(r'<div[^>]*id=[\'"]' + panel_id + r'[\'"][^>]*>(.*?)</div>\s*<!--\s*end ' + panel_id, text, re.DOTALL)
    if not m:
        # try without comment
        m = re.search(r'<div[^>]*id=[\'"]' + panel_id + r'[\'"][^>]*>(.*?)(?=<div[^>]*id=[\'"]sub-|\s*</section>)', text, re.DOTALL)
    if m:
        print(f"\n=== {panel_id} === (length: {len(m.group(0))} chars)")
        print(m.group(0)[:600] + "...")
