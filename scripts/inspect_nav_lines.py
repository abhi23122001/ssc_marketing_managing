with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '#nav .item' in l or 'dataset.sec' in l:
        print(f"Line {i+1}:")
        for j in range(max(0, i-5), min(len(lines), i+25)):
            print(f"  {j+1}: {lines[j]}", end='')
        print("\n" + "="*50)
