with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in dashboard.html: {len(lines)}")
for j in range(max(0, len(lines) - 45), len(lines)):
    print(f"  {j+1}: {lines[j]}", end='')
