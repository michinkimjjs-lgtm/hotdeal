from crawler import FMKoreaCrawler, URL, KEY
import logging
import sys

# Windows console encoding fix
sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO)

def test_meta_order():
    print("=== Testing FMKorea Meta Tag Order ===")
    crawler = FMKoreaCrawler(URL, KEY)
    
    # We want to inspect the content_html before saving, but since we can't easily hook into save_deal without mocking,
    # we'll just run crawl(limit=1) and check the logs if we add a log.
    # Actually, let's just run it and check the DB or modify crawler temporarily to print.
    # To avoid modifying crawler again, I will override the save_deal method in this script instance.
    
    original_save = crawler.save_deal
    
    def mock_save(data):
        content = data.get('content', '')
        print("\n[Content Preview Start]")
        print(content[:300])
        print("[Content Preview End]\n")
        return True # Pretend success
        
    crawler.save_deal = mock_save
    
    print("Running crawl(limit=1)...")
    crawler.crawl(limit=1)

if __name__ == "__main__":
    test_meta_order()
