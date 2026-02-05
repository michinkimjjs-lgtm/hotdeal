import requests
from bs4 import BeautifulSoup
import re

url = "https://bbs.ruliweb.com/market/board/1020"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
}

try:
    res = requests.get(url, headers=headers, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')
    
    items = soup.select('table.board_list_table tr.table_body:not(.notice)')
    print(f"Found {len(items)} items.")
    
    for i, item in enumerate(items[:5]):
        print(f"\n--- Item {i+1} ---")
        title_el = item.select_one('a.subject_link')
        title = title_el.get_text().strip() if title_el else "No Title"
        print(f"Title: {title}")
        
        # 이미지 태그 찾기 (모든 가능성 염두)
        img_tags = item.find_all('img')
        for j, img in enumerate(img_tags):
            print(f"  Img {j} attrs: {img.attrs}")
            
        # 클래스 기반 찾기
        thumb_td = item.select_one('td.thumb')
        if thumb_td:
            print(f"  td.thumb inner HTML: {thumb_td.decode_contents()[:100]}...")
            
except Exception as e:
    print(f"Error: {e}")
