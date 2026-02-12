import requests
from bs4 import BeautifulSoup
import sys
import io

# utf-8 output setting
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def debug_images():
    # 1. Get a link
    list_url = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"Fetching List: {list_url}")
    res = requests.get(list_url, headers=headers)
    res.encoding = 'euc-kr'
    
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Find a post
    target_link = None
    items = soup.select('tr.baseList')
    for item in items:
        if 'baseNotice' in item.get('class', []): continue
        title_el = item.select_one('.baseList-title')
        if title_el:
            href = title_el['href']
            target_link = ("https://www.ppomppu.co.kr" + href) if href.startswith('/') else ("https://www.ppomppu.co.kr/zboard/" + href)
            break
            
    if not target_link:
        print("No items found.")
        return

    print(f"Fetching Detail: {target_link}")
    res = requests.get(target_link, headers=headers)
    res.encoding = 'euc-kr'
    d_soup = BeautifulSoup(res.text, 'html.parser')
    
    # Extract content
    target = d_soup.select_one('table.pic_bg table td.han')
    if not target:
        target = d_soup.select_one('.board-contents') or d_soup.find('td', class_='board-contents')
        
    if target:
        print("\n[Found Images]")
        imgs = target.select('img')
        for img in imgs:
            print(f"Original Src: {img.get('src')}")
            # print(f"Tag: {img}")
    else:
        print("Content area not found.")

if __name__ == "__main__":
    debug_images()
