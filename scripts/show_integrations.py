with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx1 = text.find('id="sec-integrations"')
idx2 = text.find('id="sec-settings"')
print("Length of sec-integrations:", idx2 - idx1)
print(text[idx1:idx1+2500])
