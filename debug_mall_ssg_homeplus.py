from crawler import FMKoreaCrawler, URL, KEY
import re

crawler = FMKoreaCrawler(URL, KEY)
crawler.start_browser()

target_url = "https://www.fmkorea.com/9481535117"

try:
    print(f"Fetching {target_url}...")
    content_html = crawler.fetch_page_with_playwright(target_url)
    
    if content_html:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content_html, 'html.parser')
        
        # 1. Check Info Div
        info_div = soup.select_one('.hotdeal_info')
        if info_div:
            print(f"Info Div Text: {info_div.get_text().strip()}")
        
        # 2. Extract Buy Link (using crawler logic)
        link_el = soup.select_one('a.hotdeal_url')
        buy_link = None
        if link_el:
             href = link_el.get('href')
             print(f"Raw Href: {href}")
             # Simulate extraction logic
             if 'link.fmkorea.org' in href and 'url=' in href:
                 from urllib.parse import urlparse, parse_qs
                 try:
                    parsed = urlparse(href)
                    qs = parse_qs(parsed.query)
                    if 'url' in qs:
                        buy_link = qs['url'][0]
                 except: buy_link = href
             else:
                 buy_link = href
        
        print(f"Extracted Buy Link: {buy_link}")
        
        if buy_link:
            mall_name = crawler.extract_mall_name_from_url(buy_link)
            print(f"Mall Name (Currently): {mall_name}")
            
            # Check for redirect
            print("Checking Redirects...")
            try:
                page = crawler.context.new_page()
                page.goto(buy_link, timeout=15000, wait_until="domcontentloaded")
                final_url = page.url
                print(f"Final URL: {final_url}")
                final_mall = crawler.extract_mall_name_from_url(final_url)
                print(f"Final Mall Name: {final_mall}")
                page.close()
            except Exception as e:
                print(f"Redirect Check Failed: {e}")
            
            # 4. Check if text fallback would have worked
            if not mall_name and info_div:
                 shop_match = re.search(r'쇼핑몰\s*:\s*([^\s<]+)', info_div.get_text())
                 if shop_match:
                     print(f"Mall Name (Text Fallback): {shop_match.group(1)}")

finally:
    crawler.stop_browser()
