import requests
import time
import random

def test_gentle():
    print("=== FMKorea Gentle Verification (Mobile UA) ===")
    
    # 1. Use Mobile UA (sometimes less strict)
    mobile_ua = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36"
    
    headers = {
        'User-Agent': mobile_ua,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'https://www.google.com/' 
    }
    
    # 2. Try a different recent deal if possible, or the same one (9473693978 is known)
    # Let's try the main list page first, very gently
    url = "https://www.fmkorea.com/hotdeal"
    
    print(f"Fetching {url}...")
    try:
        res = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {res.status_code}")
        
        if res.status_code == 200:
            print("SUCCESS: List page accessed!")
            if '핫딜' in res.text:
                print("Content verified: '핫딜' found.")
            else:
                print("Warning: '핫딜' text not found (Captcha?)")
        elif res.status_code == 430:
            print("BLOCK: 430 Error (IP Blocked)")
        else:
            print(f"FAIL: {res.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gentle()
