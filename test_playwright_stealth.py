from playwright.sync_api import sync_playwright
import time
import random

def run():
    print("Starting Playwright Stealth Test...")
    with sync_playwright() as p:
        # Launch with arguments that hide automation
        browser = p.chromium.launch(
            headless=True, # Try headless first. If fails, we might need new-headless or headful (not possible on cloud easily)
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-infobars",
                "--window-position=0,0",
                "--ignore-certifcate-errors",
                "--ignore-certifcate-errors-spki-list",
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            locale="ko-KR",
            timezone_id="Asia/Seoul"
        )
        
        # Init script to further hide webdriver
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.navigator.chrome = {
                runtime: {},
                # etc.
            };
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
        """)

        page = context.new_page()
        
        print("Navigating to FMKorea Hotdeal...")
        try:
            page.goto("https://www.fmkorea.com/hotdeal", timeout=30000, wait_until="domcontentloaded")
            
            # Wait a bit for Cloudflare to solve
            print("Waiting for potential Cloudflare challenge...")
            time.sleep(5)
            
            title = page.title()
            print(f"Page Title: {title}")
            
            # Check content
            content = page.content()
            if "hotdeal_info" in content or "fm_best_widget" in content:
                 print("SUCCESS: Found hotdeal content!")
            else:
                 print("FAILURE: Hotdeal content not found.")
                 print(f"Content Preview: {content[:200]}")

        except Exception as e:
            print(f"Error: {e}")
            
        browser.close()

if __name__ == "__main__":
    run()
