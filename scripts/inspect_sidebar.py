# scripts/inspect_sidebar.py
with open("foundation/dashboard/dashboard.html", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        if 'class="item"' in line or 'data-sec=' in line:
            print(f"{idx+1}: {line.strip()}")
