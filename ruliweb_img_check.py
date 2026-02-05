import requests
from bs4 import BeautifulSoup

url = 'https://bbs.ruliweb.com/market/board/1020'
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

items = soup.select('table.board_list_table tr.table_body:not(.notice)')
for i, item in enumerate(items[:3]):
    img_el = item.select_one('img.thumb')
    if img_el:
        print(f"Item {i} Image attributes: {img_el.attrs}")
    else:
        print(f"Item {i} No img.thumb found")
