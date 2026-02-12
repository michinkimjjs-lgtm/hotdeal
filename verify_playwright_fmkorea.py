from playwright.sync_api import sync_playwright
import time

def verify_access():
    print("=== Testing FMKorea Access with Playwright ===")
    
    with sync_playwright() as p:
        # Launch browser (headless=True for production, but maybe False for debug if needed)
        # We start with headless=True as that's the goal.
        browser = p.chromium.launch(headless=True)
        
        # Use a realistic User-Agent context
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        page = context.new_page()
        
        try:
            url = "https://www.fmkorea.com/hotdeal"
            print(f"Navigating to {url}...")
            
            # Goto with timeout
            response = page.goto(url, timeout=30000, wait_until="domcontentloaded")
            
            # Wait a bit for JS to maybe render something
            page.wait_for_timeout(2000)
            
            title = page.title()
            print(f"Page Title: {title}")
            
            content = page.content()
            
            if "핫딜" in title or "핫딜" in content:
                print("✅ Success! '핫딜' found in page.")
            else:
                print("❌ '핫딜' NOT found.")
                print("Content preview:")
                print(content[:500])
                
            if response:
                print(f"Response Status: {response.status()}")
                
        except Exception as e:
            print(f"Error: {e}")
            
        finally:
            browser.close()

if __name__ == "__main__":
    verify_access()
