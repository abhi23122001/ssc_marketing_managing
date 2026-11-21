# scripts/verify_live_dashboard_html.py
import urllib.request

url = "http://127.0.0.1:8899/"
req = urllib.request.Request(url)
with urllib.request.urlopen(req) as resp:
    content = resp.read().decode('utf-8')

elements = [
    'id="global-search-input"',
    'id="btn-theme-toggle"',
    'id="sub-mkt-ai-image"',
    'id="sub-mkt-ai-video"',
    'id="sub-settings-sheets"',
    'id="sheets-tables-grid"',
    'renderAiImageStudio',
    'renderAiVideoStudio',
    'renderGoogleSheetsSettings'
]

print(f"HTTP GET {url} Status: {resp.status}, Content Length: {len(content)}")
for el in elements:
    assert el in content, f"Missing element in live server response: {el}"
    print(f"Verified live element: {el}")

print("\nALL LIVE DASHBOARD ELEMENTS FULLY VERIFIED ON PORT 8899!")
