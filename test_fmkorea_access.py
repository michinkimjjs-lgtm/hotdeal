
import requests
import random

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
]

headers = {
    'User-Agent': random.choice(user_agents),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Referer': 'https://www.fmkorea.com/hotdeal' 
}

# Target ID from user's screenshot: 9463319102
# Convert to full URL format
url_short = "https://www.fmkorea.com/9463319102"
url_full = "https://www.fmkorea.com/index.php?mid=hotdeal&document_srl=9463319102"

print(f"--- Testing Short URL: {url_short} ---")
res1 = requests.get(url_short, headers=headers)
print(f"Status: {res1.status_code}, Length: {len(res1.text)}")
if 'rd_body' in res1.text: print("SUCCESS: Detail page loaded")
else: print("FAIL: Likely redirected to list")

print(f"\n--- Testing Full URL: {url_full} ---")
res2 = requests.get(url_full, headers=headers)
print(f"Status: {res2.status_code}, Length: {len(res2.text)}")
if 'rd_body' in res2.text: print("SUCCESS: Detail page loaded")
else: print("FAIL: Likely redirected to list")
print(f"\n--- Testing List URL: https://www.fmkorea.com/hotdeal ---")
res3 = requests.get("https://www.fmkorea.com/hotdeal", headers=headers)
print(f"Status: {res3.status_code}, Length: {len(res3.text)}")
if res3.status_code == 200: print("SUCCESS: List page loaded")
else: print(f"FAIL: {res3.status_code}")
