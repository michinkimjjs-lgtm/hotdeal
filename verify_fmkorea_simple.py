import sys
import io
import logging
from crawler import FMKoreaCrawler

# 로깅 설정
logging.basicConfig(level=logging.INFO)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_existing_crawler():
    print("=== Testing Existing FMKoreaCrawler ===")
    crawler = FMKoreaCrawler("http://mock", "mock")
    # We just want to see if fetch_page works
    url = "https://www.fmkorea.com/hotdeal"
    html = crawler.fetch_page(url)
    
    if html:
        print(f"Fetch SUCCESS! Length: {len(html)}")
        print(f"Preview: {html[:200]}...")
    else:
        print("Fetch FAILED.")

if __name__ == "__main__":
    test_existing_crawler()
