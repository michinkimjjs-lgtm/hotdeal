from crawler import FMKoreaCrawler, URL, KEY
import logging
import sys

# Windows console encoding fix
sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO)

def debug_ppomppu():
    print("=== Debugging Ppomppu TLS Access ===")
    
    crawler = FMKoreaCrawler(URL, KEY)
    url = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
    
    print(f"Fetching {url}...")
    html = crawler.fetch_page(url, encoding='auto')
    
    if html:
        # html variable here is actually just the result of 'auto' which might be wrong
        # Let's get raw content to test manually
        print(f"Initial Result Len: {len(html)}")
        
        # We need raw response to test encodings. fetch_page returns decoded string.
        # Let's modify this script to use crawler.session directly
    else:
        print("fetch_page returned None")

    print("\n--- Direct Session Test ---")
    session = crawler.session
    try:
        r = session.get(url, headers={'Accept-Encoding': 'gzip, deflate'})
        print(f"Status: {r.status_code}")
        content = r.content
        print(f"Raw Content Len: {len(content)}")
        
        encodings = ['euc-kr', 'cp949', 'utf-8', 'iso-8859-1']
        for enc in encodings:
            print(f"\nDecoding with {enc}...")
            try:
                decoded = content.decode(enc)
                import re
                title_match = re.search(r'<title>(.*?)</title>', decoded, re.IGNORECASE)
                title = title_match.group(1) if title_match else "No Title Found"
                print(f"Title ({enc}): {title}")
                
                if "뽐뿌" in decoded:
                    print(f"✅ Success with {enc}!")
                else:
                    print(f"❌ '{enc}' decoded but '뽐뿌' not found.")
            except Exception as e:
                print(f"❌ Failed to decode with {enc}: {e}")
                
    except Exception as e:
        print(f"Session Error: {e}")

if __name__ == "__main__":
    debug_ppomppu()
