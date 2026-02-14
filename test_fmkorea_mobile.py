import requests
from curl_cffi import requests as cffi_requests
import logging

logging.basicConfig(level=logging.INFO)

url = "https://m.fmkorea.com/hotdeal"

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.google.com/',
}

print(f"Testing Requests on {url}...")
try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"[Requests] Status Code: {response.status_code}")
except Exception as e:
    print(f"[Requests] Error: {e}")

print(f"Testing curl_cffi on {url}...")
try:
    session = cffi_requests.Session(impersonate="chrome110")
    response = session.get(url, timeout=10)
    print(f"[curl_cffi] Status Code: {response.status_code}")
except Exception as e:
    print(f"[curl_cffi] Error: {e}")
