import cloudscraper
import logging

logging.basicConfig(level=logging.INFO)

try:
    print("Testing cloudscraper...")
    scraper = cloudscraper.create_scraper()
    response = scraper.get("https://www.fmkorea.com/hotdeal", timeout=15)
    print(f"[Cloudscraper] Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"[Cloudscraper] Success! Length: {len(response.content)}")
    else:
        print(f"[Cloudscraper] Failed.")
except Exception as e:
    print(f"[Cloudscraper] Error: {e}")
