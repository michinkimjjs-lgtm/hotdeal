import sys
import io
import logging
from crawler import PpomppuCrawler, FMKoreaCrawler, RuliwebCrawler

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
        print(f"   [Mock Insert] {data.get('source')} | {data['title'][:30]}... | {data.get('price')}")
        return self

def verify_all():
    print("=== Final Integration Verification ===")
    mock_db = MockSupabase()
    
    # 1. Ppomppu
    print("\n--- Testing Ppomppu ---")
    try:
        pc = PpomppuCrawler("https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu", "mock")
        pc.supabase = mock_db
        pc.crawl(limit=1)
    except Exception as e:
        print(f"Ppomppu Failed: {e}")

    # 2. FMKorea (Expected to be blocked or fail gracefully)
    print("\n--- Testing FMKorea ---")
    try:
        fc = FMKoreaCrawler("https://www.fmkorea.com/hotdeal", "mock")
        fc.supabase = mock_db
        fc.crawl(limit=1)
    except Exception as e:
        print(f"FMKorea Crashed: {e}")
        
    # 3. Ruliweb
    print("\n--- Testing Ruliweb ---")
    try:
        rc = RuliwebCrawler("https://bbs.ruliweb.com/market/board/1020", "mock")
        rc.supabase = mock_db
        rc.crawl(limit=1)
    except Exception as e:
        print(f"Ruliweb Failed: {e}")

if __name__ == "__main__":
    verify_all()
