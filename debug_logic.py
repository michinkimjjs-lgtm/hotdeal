
from urllib.parse import urlparse, parse_qs

def _resolve_real_url(url):
    """리다이렉트/단축 URL 등을 분석하여 진짜 목적지 반환"""
    if not url: return None
    
    print(f"DEBUG: Processing {url}")
    
    # 1. Reject Invalid / Internal Search Patterns
    if url.startswith('/'): 
        # Allow only if it looks like a redirect script
        if not any(x in url for x in ['link.php', 'move.php', 'surl.php']):
            print(f"DEBUG: Rejected by startswith('/') and not redirect script")
            return None
    
    if 'search_keyword=' in url or 'mid=hotdeal' in url:
        print(f"DEBUG: Rejected by search_keyword or mid=hotdeal")
        return None # Skip internal search links

    # 2. Redirect Resolution (link.php?url=...)
    if 'link.php' in url or 'move.php' in url or 'surl.php' in url:
        try:
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            for key in ['url', 'ol', 'link', 'target']:
                if key in qs:
                    return _resolve_real_url(qs[key][0]) # Recursive check
        except: pass
        
    return url

candidates = [
    "/index.php?mid=hotdeal&search_keyword=KREAM&search_target=title",
    "https://www.fmkorea.com/index.php?mid=hotdeal&search_keyword=KREAM&search_target=title"
]

print("--- Testing Candidates ---")
for c in candidates:
    res = _resolve_real_url(c)
    print(f"Input: {c}")
    print(f"Result: {res}")
    print("-" * 20)
