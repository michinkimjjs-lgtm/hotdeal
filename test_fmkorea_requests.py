import requests
import logging

logging.basicConfig(level=logging.INFO)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.google.com/',
}

try:
    print("Testing requests...")
    response = requests.get("https://www.fmkorea.com/hotdeal", headers=headers, timeout=10)
    print(f"[Requests] Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"[Requests] Success! Length: {len(response.content)}")
    else:
        print(f"[Requests] Failed.")
except Exception as e:
    print(f"[Requests] Error: {e}")
