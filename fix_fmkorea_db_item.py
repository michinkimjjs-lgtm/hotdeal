from crawler import FMKoreaCrawler, URL, KEY
import logging
import re
import urllib.parse
from bs4 import BeautifulSoup
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fix_db")

def fix_item(target_url):
    print(f"=== Fixing Item: {target_url} ===")
    
    crawler = FMKoreaCrawler(URL, KEY)
    crawler.start_browser()
    
    try:
        # 1. Fetch Page
        page_html = crawler.fetch_page_with_playwright(target_url)
        if not page_html:
            print("Failed to fetch page.")
            return

        soup = BeautifulSoup(page_html, 'html.parser')

        # 2. Extract Data (Simplified logic from crawler.py)
        # Info Div
        info_div = soup.select_one('.hotdeal_info')
        
        # Buy Link
        link_el = soup.select_one('a.hotdeal_url')
        buy_link = None
        if link_el:
             href = link_el.get('href')
             if 'link.fmkorea.org' in href and 'url=' in href:
                 try:
                    parsed = urllib.parse.urlparse(href)
                    qs = urllib.parse.parse_qs(parsed.query)
                    if 'url' in qs:
                        buy_link = qs['url'][0]
                 except: buy_link = href
             else:
                 buy_link = href
        
        # Mall Name
        mall_name = None
        if buy_link:
            mall_name = crawler.extract_mall_name_from_url(buy_link)
        
        if not mall_name and info_div:
             shop_match = re.search(r'쇼핑몰\s*:\s*([^\s<]+)', info_div.get_text())
             if shop_match:
                 mall_name = shop_match.group(1)

        print(f"Buy Link: {buy_link}")
        print(f"Mall Name: {mall_name}")

        # 3. Process Content (Replicate crawler logic)
        target = soup.select_one('.rd_body') or soup.select_one('div.rd_body')
        if not target:
            print("No content body found.")
            return

        for tag in target(['script', 'style']): tag.decompose()
        
        # Remove link/copy bar
        addr_div = target.select_one('.document_address')
        if addr_div: addr_div.decompose()
        
        for img in target.select('img'):
            img['referrerpolicy'] = 'no-referrer'
            
        content_html_body = str(target).replace('data-original=', 'src=')
        
        # Construct Meta Tags (Order: MALL_NAME then BUY_URL)
        meta_tags = ""
        if mall_name:
            meta_tags += f"<!-- MALL_NAME: {mall_name} -->"
        if buy_link:
            meta_tags += f"<!-- BUY_URL: {buy_link} -->"
            
        final_content = meta_tags + content_html_body
        
        # 4. Update DB (Update 'content' column)
        print("Updating DB 'content'...")
        res = crawler.supabase.table("hotdeals").update({
            "content": final_content
        }).eq("url", target_url).execute()
        
        print(f"Update Result: {res}")
        print("Successfully updated content with correct mall name.")

    finally:
        crawler.stop_browser()

if __name__ == "__main__":
    fix_item("https://www.fmkorea.com/9481535117")
