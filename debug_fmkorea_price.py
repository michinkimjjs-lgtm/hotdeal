from crawler import FMKoreaCrawler, URL, KEY
import logging
import time
from playwright.sync_api import sync_playwright

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crawler")

# Monkeypatch start_browser to use headless=False
def start_browser_visible(self):
    try:
        self.playwright = sync_playwright().start()
        # Launch visible browser
        self.browser = self.playwright.chromium.launch(headless=False) 
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
             extra_http_headers={"Referer": "https://www.fmkorea.com/hotdeal"}
        )
        logger.info("  [FMKorea] Browser Started (Visible).")
    except Exception as e:
        logger.error(f"  [FMKorea] Browser Start Failed: {e}")

FMKoreaCrawler.start_browser = start_browser_visible

crawler = FMKoreaCrawler(URL, KEY)
crawler.start_browser()

try:
    print("Fetching list page (Visible)...")
    # We main page explicitly
    page = crawler.context.new_page()
    page.goto("https://www.fmkorea.com/hotdeal", timeout=30000, wait_until="domcontentloaded")
    time.sleep(2.0)
    
    html = page.content()
    
    if html:
        from bs4 import BeautifulSoup
        import re
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select('.fm_best_widget._bd_pc li.li')
        if not items: items = soup.select('.bd_lst_wrp .bd_lst tr:not(.notice)')
        
        # Use Playwright locators for clicking
        # We need to re-query items using Playwright page object since 'soup' is static
        
        # Get locators
        # List items: .fm_best_widget._bd_pc li.li OR .bd_lst_wrp .bd_lst tr:not(.notice)
        
        page_items = page.locator('.fm_best_widget._bd_pc li.li')
        count = page_items.count()
        if count == 0:
             page_items = page.locator('.bd_lst_wrp .bd_lst tr:not(.notice)')
             count = page_items.count()
             
        print(f"Found {count} items (Playwright). Checking first 3...")
        
        for i in range(min(3, count)):
            item_loc = page_items.nth(i)
            
            # Find title link
            # Try both selectors
            link_loc = item_loc.locator('h3.title a.hotdeal_var8')
            if link_loc.count() == 0: continue
            
            title_txt = link_loc.inner_text().strip()
            print(f"\nItem {i+1}: {title_txt} (Clicking...)")
            
            # Ctrl+Click to open in new tab
            with crawler.context.expect_page() as new_page_info:
                link_loc.click(modifiers=['Control'])
                
            new_page = new_page_info.value
            new_page.wait_for_load_state("domcontentloaded")
            time.sleep(2.0)
            
            final_url = new_page.url
            print(f"  [DEBUG] Navigated to: {final_url}")
            
            d_html = new_page.content()
            new_page.close()
            
            d_soup = BeautifulSoup(d_html, 'html.parser')
            if not d_soup.select_one('.rd_body'):
                 print("  [DEBUG] WARNING: .rd_body not found! Likely List Page (Blocked?).")

            info_div = d_soup.select_one('.hotdeal_info')
            if info_div:
                p_txt = info_div.get_text()
                print(f"  [DEBUG] Raw info_div: {p_txt.strip()[:60]}...")
                p_match = re.search(r'가격\s*:\s*(?:[^\d\s]*\s*)?([0-9,]+(?:원)?)', p_txt)
                if p_match: print(f"  [DEBUG] Match: {p_match.group(1)}")
                else: print("  [DEBUG] No Regex Match")
            else:
                print("  [DEBUG] No info_div found.")

                
finally:
    pass # Keep it open briefly or close? crawler.stop_browser() closes it.
    crawler.stop_browser()
