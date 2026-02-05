import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0'}
sites = {
    "ruli": "https://bbs.ruliweb.com/market/board/1020",
    "fmk": "https://www.fmkorea.com/hotdeal",
    "ppom": "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
}

for name, url in sites.items():
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        with open(f"raw_{name}.txt", "w", encoding="utf-8") as f:
            if name == "ruli": items = soup.select('tr.table_body')
            elif name == "fmk": items = soup.select('li.li_best2_pop0')
            else: items = soup.select('tr.baseList')
            
            if items:
                f.write(items[0].prettify())
                print(f"Success: raw_{name}.txt saved.")
            else:
                f.write(res.text[:2000])
                print(f"Warning: No items found for {name}, saved header instead.")
    except Exception as e:
        print(f"Error {name}: {e}")
