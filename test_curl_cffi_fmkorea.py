from curl_cffi import requests
import time
import random

def test_curl_cffi_bypass():
    print("=== Testing FMKorea Bypass with curl_cffi ===")
    
    # Use a modern browser fingerprint
    # impersonate="chrome120" is a good default
    
    session = requests.Session(impersonate="chrome120")
    
    urls = [
        "https://www.fmkorea.com/hotdeal", # List page
        "https://www.fmkorea.com/7998666035", # Sample Deal 1 (Old)
        "https://www.fmkorea.com/9477756140", # Sample Deal 2 (New, Maxbong)
        "https://www.fmkorea.com/9473693978", # Sample Deal 3 (Jinjuham)
    ]
    
    for i, url in enumerate(urls):
        print(f"\n[{i+1}/{len(urls)}] Fetching: {url}")
        try:
            # Add a small delay like a human
            if i > 0:
                sleep_time = random.uniform(2, 4)
                print(f"Waiting {sleep_time:.2f}s...")
                time.sleep(sleep_time)
            
            response = session.get(url)
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Success!")
                if "핫딜" in response.text or "쇼핑몰" in response.text:
                    print("   Content checked: Valid")
            elif response.status_code == 430:
                print("❌ Blocked (430)")
                break
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_curl_cffi_bypass()
