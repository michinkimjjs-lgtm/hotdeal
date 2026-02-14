from curl_cffi import requests
import logging

logging.basicConfig(level=logging.INFO)

rss_url = "https://www.fmkorea.com/index.php?mid=hotdeal&act=rss"

print(f"Testing RSS URL: {rss_url}")
try:
    session = requests.Session(impersonate="chrome110")
    response = session.get(rss_url, timeout=10)
    print(f"[RSS] Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"[RSS] Success! Length: {len(response.content)}")
        print(f"[RSS] Content Preview: {response.content[:500]}")
    else:
        print(f"[RSS] Failed. {response.status_code}")
except Exception as e:
    print(f"[RSS] Error: {e}")
