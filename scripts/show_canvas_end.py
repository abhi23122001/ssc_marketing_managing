with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(2080, min(2115, len(lines))):
    print(f"{i+1}: {lines[i]}", end="")
