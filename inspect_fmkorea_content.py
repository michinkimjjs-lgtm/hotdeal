from crawler import FMKoreaCrawler, URL, KEY
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)

def inspect_content():
    print("=== Inspecting FMKorea Content for Cleanup ===")
    
    crawler = FMKoreaCrawler(URL, KEY)
    
    # Target specific URL mentioned by user or similar
    url = "https://www.fmkorea.com/9480955282" # The 'Together' ice cream link
    
    print(f"Fetching {url}...")
    html = crawler.fetch_page(url, encoding='auto')
    
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        target = soup.select_one('.rd_body') or soup.select_one('div.rd_body')
        
        if target:
            print("\n[Preview of Content Start]")
            # Print first 500 chars to see the 'copy' button structure
            print(str(target)[:1000])
            
            # Check for specific 'copy' text
            if "복사" in str(target):
                print("\n✅ Found '복사' text in content!")
            else:
                print("\n⚠️ '복사' text NOT found in .rd_body. Checking header...")
                # It might be in the title area or above rd_body?
                # Let's check parent or siblings
                
        else:
            print("❌ .rd_body not found")

if __name__ == "__main__":
    inspect_content()
