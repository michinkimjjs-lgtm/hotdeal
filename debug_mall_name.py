from crawler import FMKoreaCrawler, URL, KEY
import re

crawler = FMKoreaCrawler(URL, KEY)

# Simulation
fake_url = "https://www.sooplive.co.kr/product/12345"
fake_text = "쇼핑몰: 홈플러스 / 가격: 10000원"

print(f"URL: {fake_url}")
print(f"Text: {fake_text}")

# Current Logic
mall_name = crawler.extract_mall_name_from_url(fake_url)
print(f"Extracted from URL (Current): {mall_name}")

if not mall_name:
    shop_match = re.search(r'쇼핑몰\s*:\s*([^\s<]+)', fake_text)
    if shop_match:
        mall_name = shop_match.group(1)
        print(f"Extracted from Text (Fallback): {mall_name}")

print(f"Final Mall Name: {mall_name}")
