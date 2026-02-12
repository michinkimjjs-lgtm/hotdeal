
from bs4 import BeautifulSoup
from crawler import FMKoreaCrawler, URL, KEY

# Mock subclass to avoid init issues (we just need extract_buy_link)
class MockCrawler(FMKoreaCrawler):
    def __init__(self):
        self.user_agents = []
        pass

c = MockCrawler()

html = """
<html>
<body>
    <div class="hotdeal_info">
        <span>쇼핑몰: <a href="/index.php?mid=hotdeal&search_keyword=KREAM&search_target=title">KREAM</a></span>
        <span>가격: 1000원</span>
    </div>
    <div class="rd_body">
        <p>This is the deal.</p>
        <a href="https://www.lotteon.com/product/123456">Go to Buy</a>
        <a href="https://link.fmkorea.org/link.php?url=http%3A%2F%2Fgoogle.com">Redirect Link</a>
    </div>
</body>
</html>
"""

soup = BeautifulSoup(html, 'html.parser')

print("--- Testing extract_buy_link ---")
link = c.extract_buy_link(soup, 'FMKorea', html)
print(f"Extracted Link: {link}")

if link == "https://www.lotteon.com/product/123456":
    print("SUCCESS: Picked correct link")
elif link == "/index.php?mid=hotdeal&search_keyword=KREAM&search_target=title":
    print("FAILURE: Picked search link")
else:
    print(f"FAILURE: Picked something else: {link}")
