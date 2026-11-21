# scripts/inspect_studio.py
import re

text = open("foundation/dashboard/dashboard.html", encoding="utf-8").read()
for key in ['editor-canvas', 'editor-reel', 'ai-image', 'ai-video', 'media']:
    m = re.search(r'data-sub=[\'"]' + key + r'[\'"]', text)
    if m:
        print(f"data-sub='{key}' button found")
    p = re.search(r'id=[\'"]sub-' + key + r'[\'"]', text)
    if p:
        print(f"panel id='sub-{key}' found")

# Check canvas script functions
funcs = re.findall(r'function (drawCanvas|exportCanvas|renderReel|generateAIImage|saveProject)[a-zA-Z0-9_]*', text)
print("Canvas & studio JS functions found:", set(funcs))
