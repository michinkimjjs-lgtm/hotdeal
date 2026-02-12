import requests
from bs4 import BeautifulSoup
import re
import sys

# Encoding fix
sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
}

def fetch(url, encoding='utf-8'):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        return res.content.decode(encoding, errors='replace')
    except Exception as e:
        print(f"Fetch Error: {e}")
        return None

def debug_fmkorea(url):
    print(f"--- DEBUG FMKOREA: {url} ---")
    html = fetch(url)
    if not html: return
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Content Selector Check
    content = soup.select_one('.rd_body') or soup.find('div', class_='rd_body')
    print(f"Content Found: {bool(content)}")
    if content:
        print(f"Content length: {len(str(content))}")
    else:
        print("!! Content Selector Failed !!")
        # Dump some body classes to see what's wrong
        body = soup.find('body')
        if body: print(f"Body classes: {body.get('class')}")

    # 2. Info / Link Check
    info_div = soup.select_one('.hotdeal_info')
    print(f"Info Div Found: {bool(info_div)}")
    if info_div:
        print(f"Info Text: {info_div.get_text().strip()[:100]}...")
        link_a = info_div.select_one('a')
        if link_a:
            print(f"Link Found in Info: {link_a.get('href')}")
        else:
            print("No link in Info Div")
    else:
        print("!! Info Div Not Found !!")
        # Check if there is a table instead (older fmkorea layout?)

def debug_ppomppu(url):
    print(f"--- DEBUG PPOMPPU: {url} ---")
    html = fetch(url, encoding='euc-kr')
    if not html: return
    soup = BeautifulSoup(html, 'html.parser')

    # 1. Content Selector Check
    content = soup.select_one('table.pic_bg table td.han')
    if not content:
        content = soup.select_one('.board-contents')
    
    print(f"Content Found: {bool(content)}")
    
    # 2. Link Extraction Logic (Heuristic Test)
    links = []
    if content:
        links = content.select('a')
        print(f"Total links in content: {len(links)}")
        for a in links:
            href = a.get('href', '')
            txt = a.get_text().strip()
            if 'ppomppu' not in href and 'javascript' not in href:
                print(f"  Candidate: {href} (Text: {txt})")
                
    # 3. Check specific Ppomppu link area (top table)
    # Ppomppu usually has a link field in the table above body
    wordfix = soup.select('.wordfix a')
    print(f"Wordfix links: {[a['href'] for a in wordfix]}")

if __name__ == "__main__":
    # Use real recent URLs that failed
    # FMKorea
    debug_fmkorea('https://www.fmkorea.com/7974345242')
    # Ppomppu
    debug_ppomppu('https://www.ppomppu.co.kr/zboard/view.php?id=ppomppu&no=563531')
