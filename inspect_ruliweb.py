import requests
from bs4 import BeautifulSoup

url = "https://bbs.ruliweb.com/market/board/1020"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# 다양한 시도로 요소 찾기
rows = soup.select('tr.list_table_row')
if not rows:
    rows = soup.select('.list_table tr')

if rows:
    for row in rows[:5]:
        print("--- ROW ---")
        print(row.prettify())
        print("\n")
else:
    print("NO ROWS FOUND. Printing body start:")
    print(soup.body.prettify()[:2000])
