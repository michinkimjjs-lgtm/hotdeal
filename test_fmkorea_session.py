
import requests
import random
import time

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
]

headers = {
    'User-Agent': random.choice(user_agents),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Referer': 'https://www.google.com/' 
}

s = requests.Session()
s.headers.update(headers)

print("1. Fetching List Page...")
res1 = s.get("https://www.fmkorea.com/hotdeal")
print(f"Status: {res1.status_code}")

time.sleep(2)

target_id = "9463319102"
url = f"https://www.fmkorea.com/{target_id}"

print(f"2. Fetching Detail {url}...")
res2 = s.get(url, headers={'Referer': 'https://www.fmkorea.com/hotdeal'})
print(f"Status: {res2.status_code}")
print(f"Body Length: {len(res2.text)}")

if 'rd_body' in res2.text:
    print("SUCCESS: Found rd_body")
elif 'hotdeal_info' in res2.text:
    print("SUCCESS: Found hotdeal_info")
else:
    print("FAIL: Content not found")
