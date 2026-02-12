
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote
import re

KNOWN_MALLS = [
    'coupang', 'gmarket', 'auction', '11st', 'wemakeprice', 'tmon', 'ssg', 'lotteon', 
    'cjthemarket', 'aliexpress', 'qoo10', 'amazon', 'smartstore', 'brand.naver', 
    'shopping.naver', 'e-himart', 'gsshop', 'cjmall', 'interpark', 'lotimall', 'akmall', 
    'hyundaihmall', 'shinsegaemall', 'emart',
    # Potential missing ones
    'musinsa', 'kream', 'bucketmarket', 'taling', 'idus'
]

def _resolve_real_url(url):
    print(f"    [RESOLVE] Checking: {url}")
    if not url: return None
    
    # 1. Reject Invalid / Internal Search Patterns
    if url.startswith('/'): 
        if not any(x in url for x in ['link.php', 'move.php', 'surl.php']):
            print("    -> Rejected: Internal relative link")
            return None
    
    if 'search_keyword=' in url or 'mid=hotdeal' in url:
        print("    -> Rejected: Search link")
        return None

    # 2. Redirect Resolution
    if 'link.php' in url or 'move.php' in url or 'surl.php' in url:
        try:
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            for key in ['url', 'ol', 'link', 'target']:
                if key in qs:
                    decoded = qs[key][0]
                    print(f"      -> Decoded redirect param '{key}': {decoded}")
                    return _resolve_real_url(decoded)
        except: pass
        
    return url

def analyze_page(url_id):
    url = f"https://www.fmkorea.com/{url_id}"
    print(f"\n=== Analyzing: {url} ===")
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.content, 'html.parser')
    
    # 1. Info Div
    info_div = soup.select_one('.hotdeal_info')
    if info_div:
        print("[INFO DIV FOUND]")
        link_a = info_div.select_one('a')
        if link_a:
            href = link_a.get('href')
            print(f"  Href in InfoDiv: {href}")
            resolved = _resolve_real_url(href)
            print(f"  -> Resolved: {resolved}")
    else:
        print("[INFO DIV NOT FOUND]")
        
    # 2. Content Body
    target = soup.select_one('.rd_body') or soup.select_one('div.rd_body')
    if target:
        links = target.select('a')
        print(f"\n[CONTENT BODY] Found {len(links)} links")
        for a in links:
            href = a.get('href')
            print(f"  Candidate: {href}")
            resolved = _resolve_real_url(href)
            print(f"    -> Final: {resolved}")
            
            # Simulate KNOWN_MALLS check
            is_known = False
            for m in KNOWN_MALLS:
                if resolved and m in resolved:
                    is_known = True
                    break
            print(f"    -> Is Known Mall? {is_known}")

if __name__ == "__main__":
    analyze_page("9463319102") # Musinsa deal from screenshot
    # analyze_page("9463236439") # Ali deal
