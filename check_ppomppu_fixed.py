from crawler import PpomppuCrawler, URL, KEY
import logging
import sys

# Windows console encoding fix
sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO)

def check_ppomppu():
    print("=== Checking Ppomppu (Requests) ===")
    
    crawler = PpomppuCrawler(URL, KEY) # Uses BaseCrawler (requests)
    
    print(f"Session Type: {type(crawler.session)}") # Should be requests.sessions.Session
    
    url = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
    print(f"Fetching {url}...")
    html = crawler.fetch_page(url, encoding='euc-kr') # Ppomppu uses euc-kr
    
    if html and "뽐뿌" in html:
        print("✅ Success! '뽐뿌' found.")
        print(f"Preview: {html[:200]}...")
    else:
        print("❌ Failed.")
        if html: print(f"Preview: {html[:200]}")

if __name__ == "__main__":
    check_ppomppu()
