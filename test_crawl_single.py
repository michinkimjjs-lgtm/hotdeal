
import logging
import sys
from crawler import PpomppuCrawler, FMKoreaCrawler, RuliwebCrawler, URL, KEY

# Replace logger with one that prints to stdout
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("crawler")

def mock_save_deal(self, data):
    print("\n" + "="*50)
    print(f"[{data.get('source')}] {data.get('title')}")
    print(f"Price: {data.get('price')}")
    print(f"Category: {data.get('category')}")
    print(f"Content Length: {len(data.get('content'))}")
    
    # Extract Buy Link from content comment
    import re
    match = re.search(r'<!-- BUY_URL: (.*?) -->', data.get('content', ''))
    if match:
        print(f"✅ EXTRACTED BUY LINK: {match.group(1)}")
        
        # Check Mall Name comment
        mall_match = re.search(r'<!-- MALL_NAME: (.*?) -->', data.get('content', ''))
        if mall_match:
            print(f"✅ DETECTED MALL: {mall_match.group(1)}")
        else:
            print(f"⚠️ NO MALL DETECTED")
    else:
        print(f"❌ NO BUY LINK EXTRACTED")
        print(f"Content Snippet: {data.get('content', '')[:500]}")
        
    print("="*50 + "\n")
    return True

# Patch save_deal
PpomppuCrawler.save_deal = mock_save_deal
FMKoreaCrawler.save_deal = mock_save_deal
RuliwebCrawler.save_deal = mock_save_deal

def run_test():
    print("Starting Single Item Crawl Test...\n")
    
    # 1. Ppomppu
    try:
        p = PpomppuCrawler(URL, KEY)
        p.crawl(limit=1)
    except Exception as e:
        print(f"Ppomppu Failed: {e}")

    # 2. FMKorea
    try:
        f = FMKoreaCrawler(URL, KEY)
        f.crawl(limit=1)
    except Exception as e:
        print(f"FMKorea Failed: {e}")

    # 3. Ruliweb
    try:
        r = RuliwebCrawler(URL, KEY)
        r.crawl(limit=1)
    except Exception as e:
        print(f"Ruliweb Failed: {e}")

if __name__ == "__main__":
    run_test()
