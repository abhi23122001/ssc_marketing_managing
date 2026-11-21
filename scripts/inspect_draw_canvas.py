# scripts/inspect_draw_canvas.py
with open("foundation/dashboard/dashboard.html", encoding="utf-8") as f:
    lines = f.readlines()

print("".join(lines[3300:3460]))
