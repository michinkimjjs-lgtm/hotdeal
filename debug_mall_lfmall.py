from crawler import FMKoreaCrawler, URL, KEY
import re

crawler = FMKoreaCrawler(URL, KEY)

# Simulation: LF Mall URL
# Case 1: Standard LF Mall URL
fake_url_1 = "https://www.lfmall.co.kr/product.do?cmd=getProductDetail&PROD_CD=..."
# Case 2: LF Mall URL that might contain 'gmarket' string? Unlikely but let's test.
fake_url_2 = "https://www.lfmall.co.kr/p/gmarket_deal" 

fake_text = "쇼핑몰: G마켓 / 가격: 50000원" 

print(f"URL 1: {fake_url_1}")
print(f"Text: {fake_text}")

mall_name_1 = crawler.extract_mall_name_from_url(fake_url_1)
print(f"Extracted 1 (Current): {mall_name_1}")

if not mall_name_1:
    shop_match = re.search(r'쇼핑몰\s*:\s*([^\s<]+)', fake_text)
    if shop_match:
        print(f"Extracted 1 Text (Fallback): {shop_match.group(1)}")

print("-" * 20)

print(f"URL 2: {fake_url_2}")
mall_name_2 = crawler.extract_mall_name_from_url(fake_url_2)
print(f"Extracted 2 (Current): {mall_name_2}")
if not mall_name_2:
     shop_match = re.search(r'쇼핑몰\s*:\s*([^\s<]+)', fake_text)
     if shop_match:
        print(f"Extracted 2 Text (Fallback): {shop_match.group(1)}")
