# scripts/inspect_studio_js.py
with open("foundation/dashboard/dashboard.html", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "drawCanvas" in line or "renderStudioReel" in line or "btn-canvas-export" in line:
        print(f"Line {idx+1}: {line.strip()}")
