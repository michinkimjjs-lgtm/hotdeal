from playwright.sync_api import sync_playwright
import time

try:
    print("Starting Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        # Stealth: Hide navigator.webdriver
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("Navigating to FMKorea...")
        page.goto("https://www.fmkorea.com/hotdeal", timeout=30000)
        
        # Check for Challenge
        title = page.title()
        print(f"Page Title: {title}")
        
        if "Just a moment" in title or "Cloudflare" in title:
            print("Cloudflare Challenge Detected! Waiting...")
            time.sleep(10)
            print(f"Title after wait: {page.title()}")
        
        content = page.content()
        print(f"Content Length: {len(content)}")
        
        if len(content) > 1000 and "hotdeal_info" in content:
            print("Success! Found hotdeal content.")
        else:
            print("Failed? Content might be empty or blocked.")
            
        browser.close()
        
except Exception as e:
    print(f"Error: {e}")
