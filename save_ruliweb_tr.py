import requests
from bs4 import BeautifulSoup

url = "https://bbs.ruliweb.com/market/board/1020"
headers = {'User-Agent': 'Mozilla/5.0'}
res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

# 모든 img 태그 나열
imgs = soup.find_all('img')
print(f"Found {len(imgs)} img tags.")
for i, img in enumerate(imgs[:20]):
    print(f"Img {i}: {img.get('src', 'no-src')} | class: {img.get('class', 'no-class')}")

# 특정 클래스로 찾기
table = soup.select_one('table.board_list_table')
if table:
    print("\nTable found.")
    tr = table.select_one('tr.table_body')
    if tr:
        print(f"TR HTML: {tr.decode_contents()[:500]}...")
else:
    print("\nTable NOT found.")
