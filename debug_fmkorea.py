import requests
from bs4 import BeautifulSoup
import time

url = "https://www.fmkorea.com/hotdeal"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.fmkorea.com/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Upgrade-Insecure-Requests': '1',
    'Connection': 'keep-alive'
}

try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Success! Status 200")
        with open("debug_fmkorea.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Saved to debug_fmkorea.html")
    else:
        print(f"Failed with status: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
