from crawler import FMKoreaCrawler
import logging
import os

# Setup logging to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Dummy credentials (we only care about crawling logic, not saving to DB if it fails)
# But wait, save result is needed to see if price is correct.
# We can mock save_deal.

def test_sb_local():
    print("=== Testing FMKorea SB Crawl (Local) ===")
    
    # Credentials from environment or dummy
    URL = os.environ.get("SUPABASE_URL", "https://zvlntvovzffizoruwxqx.supabase.co")
    KEY = os.environ.get("SUPABASE_KEY", "dummy_key")
    
    crawler = FMKoreaCrawler(URL, KEY)
    
    # Mock save_deal to print instead of DB
    def mock_save_deal(deal):
        print(f"\n[Captured Deal] {deal['title']}")
        print(f"  - Price: {deal['price']}")
        print(f"  - Mall: {deal.get('mall_name', 'N/A')}")
        print(f"  - Link: {deal['url']}")
        return True
        
    crawler.save_deal = mock_save_deal
    
    # Run
    # limit=3 to test navigation
    crawler.crawl(limit=3)

if __name__ == "__main__":
    test_sb_local()
