import requests
from bs4 import BeautifulSoup
import time

# User-Agent is critical
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
}

def fetch(url, encoding='utf-8'):
    print(f"\n[Fetching] {url}")
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        print(f"Status Code: {res.status_code}")
        if res.status_code != 200:
            return None
        res.encoding = encoding
        return res.text
    except Exception as e:
        print(f"Error: {e}")
        return None

def check_ppomppu():
    print("=== Checking Ppomppu ===")
    list_url = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
    html = fetch(list_url, 'euc-kr')
    if not html: return
    soup = BeautifulSoup(html, 'html.parser')
    
    # Get first 3 links
    items = soup.select('tr.baseList:not(.baseNotice) .baseList-title')[:3]
    for item in items:
        link = "https://www.ppomppu.co.kr/zboard/" + item['href']
        print(f"Target: {link}")
        
        d_html = fetch(link, 'euc-kr')
        if not d_html: continue
        d_soup = BeautifulSoup(d_html, 'html.parser')
        
        # Test Selectors
        sel1 = d_soup.select_one('.board-contents')
        sel2 = d_soup.find('td', class_='board-contents')
        sel3 = d_soup.select_one('table.pic_bg table td.han')
        
        print(f"Selector .board-contents: {'FOUND' if sel1 else 'FAIL'}")
        print(f"Selector td.board-contents: {'FOUND' if sel2 else 'FAIL'}")
        print(f"Selector table.pic_bg table td.han: {'FOUND' if sel3 else 'FAIL'}")
        
        if not (sel1 or sel2 or sel3):
            print("DUMPING HTML START (First 500 chars) ---")
            print(d_html[:500])
            print("--- DUMP END")
        time.sleep(1)

def check_fmkorea():
    print("\n=== Checking FMKorea ===")
    list_url = "https://www.fmkorea.com/hotdeal"
    html = fetch(list_url)
    if not html: return
    soup = BeautifulSoup(html, 'html.parser')
    
    items = soup.select('.fm_best_widget._bd_pc li.li h3.title a.hotdeal_var8')[:3]
    if not items:
        items = soup.select('.bd_lst_wrp .bd_lst tr:not(.notice) h3.title a')[:3]

    for item in items:
        href = item['href']
        link = "https://www.fmkorea.com" + href if href.startswith('/') else href
        print(f"Target: {link}")
        
        d_html = fetch(link)
        if not d_html: continue
        d_soup = BeautifulSoup(d_html, 'html.parser')
        
        sel1 = d_soup.select_one('.rd_body')
        sel2 = d_soup.select_one('div.rd_body')
        
        print(f"Selector .rd_body: {'FOUND' if sel1 else 'FAIL'}")
        print(f"Selector div.rd_body: {'FOUND' if sel2 else 'FAIL'}")
        time.sleep(1)

def check_ruliweb():
    print("\n=== Checking Ruliweb ===")
    list_url = "https://bbs.ruliweb.com/market/board/1020?view=gallery"
    html = fetch(list_url)
    if not html: return
    soup = BeautifulSoup(html, 'html.parser')
    
    items = soup.select('div.flex_item.article_wrapper a.subject_link')[:3]
    
    for item in items:
        href = item['href']
        link = href
        # Ruliweb links are usually full absolute or relative?
        # Check href
        if not link.startswith('http'):
             link = "https://bbs.ruliweb.com" + link
             
        print(f"Target: {link}")
        
        d_html = fetch(link)
        if not d_html: continue
        d_soup = BeautifulSoup(d_html, 'html.parser')
        
        sel1 = d_soup.select_one('.view_content')
        sel2 = d_soup.select_one('.board_main_view')
        
        print(f"Selector .view_content: {'FOUND' if sel1 else 'FAIL'}")
        print(f"Selector .board_main_view: {'FOUND' if sel2 else 'FAIL'}")
        time.sleep(1)

if __name__ == "__main__":
    check_ppomppu()
    check_fmkorea()
    check_ruliweb()
