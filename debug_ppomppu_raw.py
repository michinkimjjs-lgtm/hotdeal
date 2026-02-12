import requests
from bs4 import BeautifulSoup
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_ppomppu_raw():
    url = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print("Fetching List...")
    res = requests.get(url, headers=headers)
    res.encoding = 'euc-kr'
    soup = BeautifulSoup(res.text, 'html.parser')
    
    print("Scanning for items with naked filename images...")
    
    found_count = 0
    for page in range(1, 6):
        print(f"Page {page}...")
        p_url = f"https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu&page={page}"
        res = requests.get(p_url, headers=headers)
        res.encoding = 'euc-kr'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        items = soup.select('tr.baseList')
        for item in items:
            if 'baseNotice' in item.get('class', []): continue
            title_el = item.select_one('.baseList-title')
            if not title_el: continue
            
            href = title_el['href']
            detail_url = ("https://www.ppomppu.co.kr" + href) if href.startswith('/') else ("https://www.ppomppu.co.kr/zboard/" + href)
            
            try:
                d_res = requests.get(detail_url, headers=headers, timeout=5)
                d_res.encoding = 'euc-kr'
                d_soup = BeautifulSoup(d_res.text, 'html.parser')
                
                target = d_soup.select_one('table.pic_bg table td.han')
                if not target: target = d_soup.select_one('.board-contents')
                
                if target:
                    imgs = target.select('img')
                    if imgs:
                        print(f"[{found_count+1}] Item: {title_el.get_text().strip()}")
                        print(f"URL: {detail_url}")
                        for img in imgs:
                            src = img.get('src', '')
                            print(f"  - SRC: {src}")
                        found_count += 1
                        if found_count >= 5: return
            except Exception as e:
                print(f"Error checking {detail_url}: {e}")
                
    if found_count == 0:
        print("No items with naked filenames found.")

if __name__ == "__main__":
    check_ppomppu_raw()
