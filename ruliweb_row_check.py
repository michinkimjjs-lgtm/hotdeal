import requests
from bs4 import BeautifulSoup

url = 'https://bbs.ruliweb.com/market/board/1020'
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

items = soup.select('table.board_list_table tr.table_body:not(.notice)')
for i, item in enumerate(items[:3]):
    print(f"--- Item {i} ---")
    print(item.prettify()[:1000])
