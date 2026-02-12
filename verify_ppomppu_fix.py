import sys
import io
import logging
from crawler import PpomppuCrawler

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Mock Supabase to avoid actual DB writes during verification
class MockSupabase:
    def table(self, name):
        return self
    def insert(self, data):
        print(f"\n[MockDB Insert] {data['title']}")
        print(f"  - Source: {data['source']}")
        print(f"  - Mall: {data.get('source')} (derived)")
        print(f"  - Price: {data.get('price')}")
        print(f"  - Img: {data.get('img_url')}")
        print(f"  - Buy Link In Content: {'BUY_URL' in data.get('content', '')}")
        if 'BUY_URL' in data.get('content', ''):
             # Extract buy url from comment
             import re
             m = re.search(r'BUY_URL: (http.*?) -->', data['content'])
             if m: print(f"  - Extracted URL: {m.group(1)}")
        return self
    def select(self, *args): return self
    def eq(self, *args): return self
    def update(self, data):
        print(f"\n[MockDB Update] {data['title']}")
        return self
    def execute(self):
        return type('obj', (object,), {'data': []})

def verify_ppomppu():
    print("=== Ppomppu Verification ===")
    crawler = PpomppuCrawler("http://mock", "mock")
    crawler.supabase = MockSupabase()
    
    # Overwrite crawl to use MockDB has already been handled by swapping .supabase instance
    # But wait, the original crawl method calls self.supabase...
    
    crawler.crawl(limit=1)

if __name__ == "__main__":
    verify_ppomppu()
