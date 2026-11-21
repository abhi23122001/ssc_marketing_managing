# scripts/inspect_canvas_markup.py
with open("foundation/dashboard/dashboard.html", encoding="utf-8") as f:
    lines = f.readlines()

print("".join(lines[730:860]))
