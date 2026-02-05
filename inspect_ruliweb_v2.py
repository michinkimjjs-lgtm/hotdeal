import requests
from bs4 import BeautifulSoup

url = "https://bbs.ruliweb.com/market/board/1020"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

print(f"Status Code: {response.status_code}")
print("--- ALL TR CLASSES ---")
for tr in soup.find_all('tr'):
    print(tr.get('class'))

print("\n--- FIRST FEW TR CONTENT ---")
for tr in soup.find_all('tr')[:10]:
    print(tr.get_text()[:100].strip())
    print("-" * 20)
