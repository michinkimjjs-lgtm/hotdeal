import requests
from bs4 import BeautifulSoup
url = 'https://bbs.ruliweb.com/market/board/1020'
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')
tr = soup.select_one('table.board_list_table tr.table_body:not(.notice)')
if tr:
    print("--- TR FOUND ---")
    imgs = tr.find_all('img')
    for i, img in enumerate(imgs):
        print(f"Img {i} attrs: {img.attrs}")
else:
    print("No TR found")
