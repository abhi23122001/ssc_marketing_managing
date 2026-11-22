import urllib.request
import re
import csv
import io
import json

sheet_id = "17CpMIB7mMrBalL6juZMmKVFvm2j5IvLXJjYdsbAmU5c"
htmlview_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/htmlview"

req = urllib.request.Request(htmlview_url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"HTML View Length: {len(html)}")
        title_m = re.search(r'<title>([^<]+)</title>', html)
        if title_m:
            print(f"Title: {title_m.group(1)}")
            
        # Look for sheet tab links
        tabs = re.findall(r'<li id="sheet-button-[^"]+"[^>]*><a[^>]*href="[^"]*gid=(\d+)[^"]*"[^>]*>([^<]+)</a>', html)
        print(f"Tabs by button: {tabs}")
        
        # Look for sheet names in JavaScript objects or tables
        tables = re.findall(r'<table class="waffle"[^>]*id="([^"]+)"', html)
        print(f"Tables: {tables}")
        
        # Search for any sheet titles or JSON configurations
        m = re.findall(r'"title":\s*"([^"]+)"', html)
        if m:
            print(f"Titles found in JSON: {m[:10]}")
except Exception as e:
    print(f"Error fetching htmlview: {e}")

# Check gid=0 CSV
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
try:
    with urllib.request.urlopen(urllib.request.Request(csv_url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=10) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        reader = list(csv.reader(io.StringIO(content)))
        print(f"\n--- GID 0 Rows ({len(reader)}) ---")
        for i, row in enumerate(reader[:15]):
            print(f"Row {i}: {row}")
except Exception as e:
    print(f"Error fetching GID 0: {e}")
