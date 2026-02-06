import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
}

def fetch(url, encoding='utf-8'):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code != 200: return None
        res.encoding = encoding
        return res.text
    except: return None

def inspect_ppomppu():
    print("\n--- Ppomppu Links ---")
    # Ppomppu distinct feature: '관련링크' usually in .han class or a specific pattern
    url = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
    html = fetch(url, 'euc-kr')
    if not html: return
    soup = BeautifulSoup(html, 'html.parser')
    
    # Get a post
    link = soup.select_one('tr.baseList:not(.baseNotice) .baseList-title')['href']
    full_url = "https://www.ppomppu.co.kr/zboard/" + link
    print(f"Post: {full_url}")
    
    d_html = fetch(full_url, 'euc-kr')
    d_soup = BeautifulSoup(d_html, 'html.parser')
    
    # Try finding links
    # Usually in <p class="link_source"> or similar. Or inside the body?
    # Actually Ppomppu has a 'Link: ' section at top of content sometimes.
    # Let's dump all links in the main area
    links = d_soup.select('.wordfix a')
    for l in links:
        print(f"Found .wordfix a: {l['href']}")
        
    links2 = d_soup.select('.han a')
    for l in links2[:3]:
        print(f"Found .han a: {l['href']}")

def inspect_fmkorea():
    print("\n--- FMKorea Links ---")
    url = "https://www.fmkorea.com/hotdeal"
    html = fetch(url)
    soup = BeautifulSoup(html, 'html.parser')
    item = soup.select_one('.fm_best_widget._bd_pc li.li h3.title a.hotdeal_var8')
    if not item: return
    link = "https://www.fmkorea.com" + item['href']
    print(f"Post: {link}")
    
    d_html = fetch(link)
    d_soup = BeautifulSoup(d_html, 'html.parser')
    
    # FMKorea distinct feature: '쇼핑몰 링크' might be just in the body or a specific header
    # Often it is in a table with class 'hotdeal_table' or similar?
    # Let's check links in .rd_body
    links = d_soup.select('.rd_body a')
    for l in links[:3]:
        print(f"Found .rd_body a: {l['href']}")

def inspect_ruliweb():
    print("\n--- Ruliweb Links ---")
    url = "https://bbs.ruliweb.com/market/board/1020?view=gallery"
    html = fetch(url)
    soup = BeautifulSoup(html, 'html.parser')
    item = soup.select_one('div.flex_item.article_wrapper a.subject_link')
    if not item: return
    link = item['href']
    if link.startswith('/'): link = "https://bbs.ruliweb.com" + link
    print(f"Post: {link}")
    
    d_html = fetch(link)
    d_soup = BeautifulSoup(d_html, 'html.parser')
    
    # Ruliweb has a SOURCE field
    source_link = d_soup.select_one('.source_url a')
    if source_link:
        print(f"Found .source_url a: {source_link['href']}")
        
    # Also extracted links from content
    links = d_soup.select('.view_content a')
    for l in links[:3]:
        print(f"Found .view_content a: {l['href']}")

if __name__ == "__main__":
    inspect_ppomppu()
    inspect_fmkorea()
    inspect_ruliweb()
