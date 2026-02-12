import logging
import sys
from crawler import FMKoreaCrawler

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_fmkorea_local_mock():
    print("=== Testing FMKorea Parsing with Local Mock ===")
    
    URL = "https://zvlntvovzffizoruwxqx.supabase.co"
    KEY = "sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV"
    
    crawler = FMKoreaCrawler(URL, KEY)
    
    # Load sample HTML
    with open('fmkorea_sample.html', 'r', encoding='utf-8') as f:
        sample_html = f.read()
        
    # Monkeypatch fetch_page
    def mock_fetch(url, **kwargs):
        print(f"Mock Fetching: {url}")
        # Return sample HTML for detail page logic
        # For list page logic, we need a list page?
        # The crawler fetches list page first.
        # If we return sample_html for list page, parse might fail if selectors differ.
        # But fmkorea_sample.html IS a detail page.
        # The crawl method expects a LIST (ul.li) first.
        # So we need to mock the LIST page response to return at least one item that points to a detail page.
        
        if 'hotdeal' in url and 'document_srl' not in url and '9473693978' not in url:
             # This is likely the list page request
             # Create a dummy list page HTML that points to our "detail" URL
             return """
             <html>
             <body>
                 <div class="fm_best_widget _bd_pc">
                     <ul>
                         <li class="li">
                             <h3 class="title">
                                 <a href="/9473693978" class="hotdeal_var8">Mock Item Title</a>
                             </h3>
                         </li>
                     </ul>
                 </div>
             </body>
             </html>
             """
        else:
             # Detail page request
             return sample_html

    crawler.fetch_page = mock_fetch

    # Override save_deal
    def mock_save_deal(deal):
        print("\n[SUCCESS] Deal Extracted:")
        print(f"Title: {deal['title']}")
        print(f"Price: {deal['price']}")
        print(f"Source: {deal['source']}")
        print(f"URL: {deal['url']}")
        
        # Check injected comments
        if deal['content']:
             print("Content Length:", len(deal['content']))
             if "<!-- BUY_URL: https://brand.naver.com/jinjuham/products/8391222352 -->" in deal['content']:
                 print("✅ BUY_URL Injected Correctly")
             else:
                 print("❌ BUY_URL Injection FAILED")
                 print("Preview:", deal['content'][:200])
                 
             if "<!-- MALL_NAME: 네이버 -->" in deal['content']:
                 print("✅ MALL_NAME Injected Correctly")
             else:
                  print("❌ MALL_NAME Injection FAILED")
        return True
        
    crawler.save_deal = mock_save_deal
    
    # Crawl
    crawler.crawl(limit=1)

if __name__ == "__main__":
    test_fmkorea_local_mock()
