from crawler import FMKoreaCrawler, URL, KEY
import logging

logging.basicConfig(level=logging.INFO)

def check_crawler_tls():
    print("=== Checking Modified Crawler (tls_client) ===")
    
    crawler = FMKoreaCrawler(URL, KEY)
    
    # Check session type
    print(f"Session Type: {type(crawler.session)}")
    
    # Try fetching list page
    print("Fetching Ppomppu List Page...")
    html = crawler.fetch_page("https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu", encoding='auto')
    
    if html and "뽐뿌" in html:
        print("✅ Success! Content fetched and decoded.")
        print(f"Preview: {html[:100]}...")
    else:
        print("❌ Failed to fetch or decode content.")
        if html:
             print(f"HTML Preview (Error?): {html[:200]}")

if __name__ == "__main__":
    check_crawler_tls()
