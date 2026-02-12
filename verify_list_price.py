from crawler import FMKoreaCrawler, URL, KEY
import logging
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)

crawler = FMKoreaCrawler(URL, KEY)
crawler.start_browser()

try:
    print("Fetching list page...")
    html = crawler.fetch_page_with_playwright("https://www.fmkorea.com/hotdeal")
    
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select('.fm_best_widget._bd_pc li.li')
        if not items: items = soup.select('.bd_lst_wrp .bd_lst tr:not(.notice)')
        
        print(f"Found {len(items)} items. Checking prices from LIST view...")
        
        for i, item in enumerate(items[:5]):
            title_el = item.select_one('h3.title a.hotdeal_var8')
            if not title_el: continue
            title = title_el.get_text().strip()
            
            # Try extraction from list item
            price = "가격미상"
            info_div = item.select_one('.hotdeal_info')
            if info_div:
                import re
                p_txt = info_div.get_text()
                p_match = re.search(r'가격\s*:\s*(?:[^\d\s]*\s*)?([0-9,]+(?:원)?)', p_txt)
                if p_match: price = p_match.group(1)
            
            print(f"Item {i+1}: {price} | Title: {title[:20]}...")

finally:
    crawler.stop_browser()
