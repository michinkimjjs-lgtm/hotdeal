import tls_client
import time
import random

def test_tls_client_bypass():
    print("=== Testing FMKorea Bypass with tls_client ===")
    
    # Create a session with a Chrome fingerprint
    session = tls_client.Session(
        client_identifier="chrome_120",
        random_tls_extension_order=True
    )

    urls = [
        "https://www.fmkorea.com/hotdeal", # List page
        "https://www.fmkorea.com/7998666035", # Sample Deal 1
        "https://www.fmkorea.com/9477756140", # Sample Deal 2
        "https://www.fmkorea.com/9473693978", # Sample Deal 3
    ]
    
    for i, url in enumerate(urls):
        print(f"\n[{i+1}/{len(urls)}] Fetching: {url}")
        try:
            if i > 0:
                sleep_time = random.uniform(2, 4)
                print(f"Waiting {sleep_time:.2f}s...")
                time.sleep(sleep_time)
            
            # tls_client uses .get() similar to requests
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
    test_tls_client_bypass()
