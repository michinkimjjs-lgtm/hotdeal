
import requests
import random
import time

url = "https://www.fmkorea.com/9463319102"

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
]

headers = {
    'User-Agent': random.choice(user_agents),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Referer': 'https://www.google.com/'
}

print(f"Fetching {url}...")
try:
    res = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {res.status_code}")
    print(f"Content Length: {len(res.text)}")
    
    with open('debug_fmkorea.html', 'w', encoding='utf-8') as f:
        f.write(res.text)
    print("Saved to debug_fmkorea.html")
except Exception as e:
    print(f"Error: {e}")
