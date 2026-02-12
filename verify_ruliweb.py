import sys
import io
import logging
from crawler import RuliwebCrawler

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
        print(f"\n[MockDB Insert]")
        print(f"Title: {data['title']}")
        print(f"Price: {data.get('price')}")
        print(f"Source: {data.get('source')}")
        print(f"Img: {data.get('img_url')}")
        print(f"URL: {data.get('url')}")
        return self

def verify():
    print("=== Ruliweb Final Verification ===")
    crawler = RuliwebCrawler("https://bbs.ruliweb.com/market/board/1020", "mock")
    crawler.supabase = MockSupabase()
    # Crawl 3 items to check different cases
    crawler.crawl(limit=3)

if __name__ == "__main__":
    verify()
