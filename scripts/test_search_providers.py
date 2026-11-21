import urllib.request
import urllib.parse
import re
import json

def test_ddg():
    query = "dgps surveying tolerances"
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            # find results
            results = []
            links = re.findall(r'<a[^>]+class="[^"]*result__snippet[^"]*"[^>]+href="([^"]+)"', html)
            snippets = re.findall(r'<a[^>]+class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</a>', html, re.DOTALL)
            titles = re.findall(r'<a[^>]+class="[^"]*result__title[^"]*"[^>]*>(.*?)</a>', html, re.DOTALL)
            print(f"links: {len(links)}, snippets: {len(snippets)}, titles: {len(titles)}")
            if not links:
                # check url extraction
                raw_urls = re.findall(r'href="((?:https?://|//duckduckgo\.com/l/\?uddg=)[^"]+)"', html)
                print("raw_urls found:", len(raw_urls))
                if raw_urls:
                    print("Sample raw URL:", raw_urls[0])
            return len(links) > 0 or len(snippets) > 0
    except Exception as e:
        print("DDG Error:", e)
        return False

test_ddg()
