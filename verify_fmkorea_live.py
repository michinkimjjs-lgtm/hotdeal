import logging
import sys
from crawler import FMKoreaCrawler

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_fmkorea_live():
    print("=== Testing FMKorea Live Crawl (With Setup) ===")
    
    # Use real credentials from crawler.py
    URL = "https://zvlntvovzffizoruwxqx.supabase.co"
    KEY = "sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV"
    
    crawler = FMKoreaCrawler(URL, KEY)
    
    # Monkeypatch fetch_page to capture HTML
    original_fetch = crawler.fetch_page
    
    def side_effect_fetch(url, **kwargs):
        print(f"Fetching: {url}")
        res = original_fetch(url, **kwargs)
        if res:
            # Check if this is a detail page (contains digits)
            # URL: https://www.fmkorea.com/9473932423
            if "www.fmkorea.com/" in url and any(c.isdigit() for c in url.split('/')[-1]):
                 print(f"Captured Detail HTML for {url}")
                 with open('fmkorea_debug_detail.html', 'w', encoding='utf-8') as f:
                     f.write(res)
        return res

    crawler.fetch_page = side_effect_fetch

    # Override save_deal to just print instead of saving to DB
    def mock_save_deal(deal):
        print("\n[SUCCESS] Deal Extracted:")
        print(f"Title: {deal['title']}")
        print(f"Price: {deal['price']}")
        print(f"Source: {deal['source']}")
        print(f"URL: {deal['url']}")
        if 'BUY_URL' in deal['content']:
            print("Buy Link: Found in content")
        else:
            print("Buy Link: NOT FOUND")
        return True
        
    crawler.save_deal = mock_save_deal
    
    # Crawl 1 item
    crawler.crawl(limit=1)

if __name__ == "__main__":
    test_fmkorea_live()
