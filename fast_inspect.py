import requests
from bs4 import BeautifulSoup

url = "https://bbs.ruliweb.com/market/board/1020"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}

res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

# 테이블 검색
table = soup.select_one('table.board_list_table')
if table:
    print(f"Table found! Rows: {len(table.find_all('tr'))}")
    for tr in table.find_all('tr')[:15]:
        print(f"TR Class: {tr.get('class')} | Text: {tr.get_text()[:50].strip()}")
else:
    print("board_list_table NOT found.")
