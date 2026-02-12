import requests
import random

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Referer': 'https://www.fmkorea.com/hotdeal' 
}

url = "https://www.fmkorea.com/9473932423"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    with open('fmkorea_debug.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("Saved to fmkorea_debug.html")
else:
    print(f"Failed: {response.status_code}")
