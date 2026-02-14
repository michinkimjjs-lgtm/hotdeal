from curl_cffi import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test")

def test_impersonate(browser_type):
    print(f"Testing {browser_type}...")
    try:
        session = requests.Session(impersonate=browser_type)
        response = session.get("https://www.fmkorea.com/hotdeal", timeout=10)
        print(f"[{browser_type}] Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"[{browser_type}] Success! Length: {len(response.content)}")
            return True
        else:
            print(f"[{browser_type}] Failed.")
    except Exception as e:
        print(f"[{browser_type}] Error: {e}")
    return False

browsers = [
    "chrome120",
    "chrome110",
    "edge99",
    "safari15_3",
    "safari17_0",
]

print("=== Starting FMKorea Connection Test (Local) ===")
for b in browsers:
    if test_impersonate(b):
        break
