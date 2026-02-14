from curl_cffi import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test")

def test_impersonate(browser_type, use_headers=False):
    print(f"Testing {browser_type} (Headers={use_headers})...")
    try:
        headers = None
        if use_headers:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.google.com/',
            }

        session = requests.Session(impersonate=browser_type)
        response = session.get("https://www.fmkorea.com/hotdeal", headers=headers, timeout=10)
        print(f"[{browser_type}|Headers={use_headers}] Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"[{browser_type}] Success! Length: {len(response.content)}")
            return True
        else:
            print(f"[{browser_type}] Failed.")
    except Exception as e:
        print(f"[{browser_type}] Error: {e}")
    return False

browsers = [
    "chrome110",
    "edge99",
    "safari15_3",
]

print("=== Starting FMKorea Header Test (Local) ===")
for b in browsers:
    test_impersonate(b, use_headers=False)
    test_impersonate(b, use_headers=True) # Check if adding headers breaks it
