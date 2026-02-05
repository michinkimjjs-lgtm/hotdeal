import requests
from bs4 import BeautifulSoup
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# 1. Ruliweb Check
print("--- Ruliweb Check ---")
res = requests.get("https://bbs.ruliweb.com/market/board/1020", headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')
items = soup.select('table.board_list_table tr.table_body:not(.notice)')
for i, item in enumerate(items[:3]):
    print(f"Item {i}: Title={item.select_one('.subject_link').get_text().strip() if item.select_one('.subject_link') else 'None'}")
    img = item.find('img')
    print(f"  Img: {img.attrs if img else 'None'}")
    thumb_td = item.select_one('td.thumb')
    print(f"  td.thumb present: {thumb_td is not None}")

# 2. FMKorea Check (Price fix)
print("\n--- FMKorea Check ---")
res = requests.get("https://www.fmkorea.com/hotdeal", headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')
items = soup.select('li.li_best2_pop0')
for i, item in enumerate(items[:3]):
    title = item.select_one('.title a').get_text().strip() if item.select_one('.title a') else "None"
    info = item.select_one('.hotdeal_info')
    price_el = info.select('span') if info else []
    # Find span containing '가격:' or similar
    price = "Not Found"
    for s in price_el:
        if '가격:' in s.get_text():
            price = s.select_one('a.strong').get_text().strip() if s.select_one('a.strong') else s.get_text()
    print(f"Item {i}: Title={title} | Price={price}")

# 3. Ppomppu Check
print("\n--- Ppomppu Check ---")
res = requests.get("https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu", headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')
items = soup.select('tr.baseList:not(.notice)')
for i, item in enumerate(items[:3]):
    title = item.select_one('.baseList-title').get_text().strip() if item.select_one('.baseList-title') else "None"
    img = item.select_one('.baseList-thumb img')
    print(f"Item {i}: Title={title} | Img={img['src'] if img else 'None'}")
