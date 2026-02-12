import sys
import io
import logging
import time
from crawler import PpomppuCrawler, FMKoreaCrawler, RuliwebCrawler, URL, KEY

# 로깅 설정 (콘솔 출력 강제)
logging.basicConfig(level=logging.INFO)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def deploy_test():
    print("=== 🚀 Live Deployment Test (One Item Each) ===")
    print(f"Target DB: {URL}")
    
    # 1. Ppomppu
    print("\n[1/3] Crawling Ppomppu...")
    try:
        pc = PpomppuCrawler(URL, KEY)
        # Limit 1 to just get one item
        pc.crawl(limit=1)
        print("✅ Ppomppu Done")
    except Exception as e:
        print(f"❌ Ppomppu Failed: {e}")

    time.sleep(2)

    # 2. FMKorea
    print("\n[2/3] Crawling FMKorea...")
    try:
        fc = FMKoreaCrawler(URL, KEY)
        fc.crawl(limit=1)
        print("✅ FMKorea Done")
    except Exception as e:
        print(f"❌ FMKorea Failed: {e}")

    time.sleep(2)

    # 3. Ruliweb
    print("\n[3/3] Crawling Ruliweb...")
    try:
        rc = RuliwebCrawler(URL, KEY)
        rc.crawl(limit=1)
        print("✅ Ruliweb Done")
    except Exception as e:
        print(f"❌ Ruliweb Failed: {e}")

    print("\n=== ✨ Deployment Test Completed ===")
    print("Please check your website to verify the new items.")

if __name__ == "__main__":
    deploy_test()
