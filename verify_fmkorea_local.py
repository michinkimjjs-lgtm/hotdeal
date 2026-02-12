import sys
import io
import logging
from crawler import FMKoreaCrawler
from unittest.mock import MagicMock

# 로깅 설정
logging.basicConfig(level=logging.INFO)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Mock Supabase
class MockSupabase:
    def table(self, name): return self
    def select(self, *args): return self
    def eq(self, *args): return self
    def update(self, data): return self
    def execute(self): return type('obj', (object,), {'data': []})
    def insert(self, data):
        print(f"\n[MockDB Insert] {data['title']}")
        print(f"  - Price: {data.get('price')}")
        print(f"  - Source: {data.get('source')}")
        print(f"  - Img: {data.get('img_url')}")
        print(f"  - Buy Link In Content: {'BUY_URL' in data.get('content', '')}")
        if 'BUY_URL' in data.get('content', ''):
             import re
             m = re.search(r'BUY_URL: (http.*?) -->', data['content'])
             if m: print(f"  - Extracted URL: {m.group(1)}")
        return self

class LocalFMKoreaCrawler(FMKoreaCrawler):
    def fetch_page(self, url, encoding='utf-8', retries=3, referer=None):
        if "hotdeal" in url and "9473693978" not in url:
            # Main list page mock - returns a simple list with 1 item pointing to our detail
            return """
            <html><body>
            <div class="fm_best_widget _bd_pc">
                <li class="li">
                    <h3 class="title"><a href="/9473693978" class="hotdeal_var8">Test Item</a></h3>
                    <div class="hotdeal_info">가격: 10,000원</div>
                </li>
            </div>
            </body></html>
            """
        elif "9473693978" in url:
            # Detail page - read from local file
            try:
                with open("fmkorea_sample.html", "r", encoding="utf-8") as f:
                    return f.read()
            except:
                return ""
        return ""

def verify():
    print("=== FMKorea Local Verification ===")
    crawler = LocalFMKoreaCrawler("http://mock", "mock")
    crawler.supabase = MockSupabase()
    crawler.crawl(limit=1)

if __name__ == "__main__":
    verify()
