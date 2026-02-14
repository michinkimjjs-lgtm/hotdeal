from playwright.sync_api import sync_playwright
import time
import random

def run():
    print("Starting Playwright Stealth Test (Refined)...")
    with sync_playwright() as p:
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-infobars",
            "--window-position=0,0",
            "--ignore-certificate-errors",
            "--ignore-certificate-errors-spki-list",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        # Launch with ignore_default_args to remove 'enable-automation' banner/flag
        browser = p.chromium.launch(
            headless=True,
            args=args,
            ignore_default_args=["--enable-automation"]
        )
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            locale="ko-KR",
            timezone_id="Asia/Seoul",
            java_script_enabled=True,
        )
        
        # Init script: Hide webdriver + Permissions
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Overwrite the `plugins` property to use a custom getter.
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });

            // Pass the Webdriver Test.
            const newProto = navigator.__proto__;
            delete newProto.webdriver;
            navigator.__proto__ = newProto;
        """)

        page = context.new_page()
        
        print("Navigating to FMKorea Hotdeal...")
        try:
            # 1. Go to homepage first (to build cookies?)
            # page.goto("https://www.fmkorea.com/", timeout=30000)
            # time.sleep(2)
            
            # 2. Go to Hotdeal
            response = page.goto("https://www.fmkorea.com/hotdeal", timeout=30000, wait_until="domcontentloaded")
            print(f"Status: {response.status}")
            
            # Cloudflare Wait
            print("Waiting for Cloudflare/Loading...")
            time.sleep(5)
            
            # Mouse Movement Simulation
            print("Simulating Mouse...")
            page.mouse.move(random.randint(100, 500), random.randint(100, 500))
            page.mouse.down()
            time.sleep(0.1)
            page.mouse.up()
            
            title = page.title()
            print(f"Page Title: {title}")
            
            content = page.content()
            if "hotdeal_info" in content or "fm_best_widget" in content:
                 print("SUCCESS: Found hotdeal content!")
                 # print(content[:1000]) # Debug
            else:
                 print("FAILURE: Hotdeal content not found.")
                 # Print first 200 chars of body
                 print(page.inner_text('body')[:200])

        except Exception as e:
            print(f"Error: {e}")
            
        browser.close()

if __name__ == "__main__":
    run()
