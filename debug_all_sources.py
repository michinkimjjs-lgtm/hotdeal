import requests
from bs4 import BeautifulSoup
import os

urls = {
    "ruliweb": "https://bbs.ruliweb.com/market/board/1020",
    "fmkorea": "https://www.fmkorea.com/hotdeal",
    "ppomppu": "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

for name, url in urls.items():
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        with open(f"debug_{name}.html", "w", encoding='utf-8') as f:
            f.write(res.text)
        print(f"Saved debug_{name}.html")
        
        soup = BeautifulSoup(res.text, 'html.parser')
        if name == 'ruliweb':
            items = soup.select('table.board_list_table tr.table_body')
            print(f"Ruliweb items found: {len(items)}")
            if items:
                print(f"First item HTML sample: {items[0].prettify()[:500]}")
        elif name == 'fmkorea':
            items = soup.select('li.li_best2_pop0')
            print(f"FMKorea items found: {len(items)}")
        elif name == 'ppomppu':
            items = soup.select('tr.baseList')
            print(f"Ppomppu items found: {len(items)}")
            
    except Exception as e:
        print(f"Error {name}: {e}")
