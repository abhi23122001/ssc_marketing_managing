import urllib.request
data = urllib.request.urlopen('http://127.0.0.1:8899/').read().decode('utf-8')
print("Found in served HTML:", 'id="ws-wshop"' in data)
idx = data.find('id="ws-wshop"')
if idx != -1:
    print("Context:", repr(data[idx-40:idx+80]))
