
import requests
from bs4 import BeautifulSoup
import re
import logging
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test")

KNOWN_MALLS = [
    'coupang.com', 'coupang.net', 'gmarket.co.kr', 'auction.co.kr', '11st.co.kr', 
    'wemakeprice.com', 'tmon.co.kr', 'ssg.com', 'lotteon.com', 'cjthemarket.com', 
    'aliexpress.com', 'qoo10.com', 'amazon.com', 'smartstore.naver.com', 'brand.naver.com',
    'shopping.naver.com', 'e-himart.co.kr', 'gsshop.com', 'cjmall.com', 'interpark.com',
    'lotimall.com', 'akmall.com', 'hyundaihmall.com', 'shinsegaemall.ssg.com', 'emart.ssg.com'
]

def extract_mall_name_from_url(url):
    """URL에서 쇼핑몰 이름 (한글) 반환"""
    if not url: return None
    if 'coupang' in url: return '쿠팡'
    if 'gmarket' in url: return 'G마켓'
    if 'auction' in url: return '옥션'
    if '11st' in url: return '11번가'
    if 'wemakeprice' in url: return '위메프'
    if 'tmon' in url: return '티몬'
    if 'ssg' in url: return 'SSG'
    if 'lotteon' in url: return '롯데온'
    if 'cj' in url and 'market' in url: return 'CJ더마켓'
    if 'ali' in url: return '알리익스프레스'
    if 'qoo10' in url: return '큐텐'
    if 'amazon' in url: return '아마존'
    if 'naver' in url: return '네이버쇼핑'
    if 'himart' in url: return '하이마트'
    if 'gsshop' in url: return 'GS SHOP'
    return None

def extract_buy_link(soup, source, content_html):
    print(f"--- Extracting for {source} ---")
    
    # 1. Ruliweb: Has explicit .source_url
    if source == 'Ruliweb':
        src_el = soup.select_one('.source_url a')
        if src_el and src_el.has_attr('href'):
            return src_el['href']

    # 2. FMKorea: Specific .hotdeal_info check
    if source == 'FMKorea':
        info_div = soup.select_one('.hotdeal_info')
        if info_div:
            link_a = info_div.select_one('a')
            if link_a and link_a.has_attr('href'):
                return link_a['href']
                
    # 3. Aggressive Scan
    c_soup = BeautifulSoup(content_html, 'html.parser')
    links = c_soup.select('a')
    
    for a in links:
        href = a.get('href', '')
        if not href: continue
        if 'adpost' in str(a.parent.get('class', [])): continue
        if 'adbiz' in href: continue

        for mall in KNOWN_MALLS:
            if mall in href:
                print(f"  [MATCH] {mall} in {href}")
                return href
    
    print("  [NO MATCH] No known mall found. Checking fallbacks...")
    # Fallback
    for a in links:
        href = a.get('href', '')
        if not href or href.startswith('#') or href.startswith('javascript'): continue
        if 'ppomppu.co.kr' in href or 'fmkorea.com' in href or 'ruliweb.com' in href: continue
        if 'naver.com' in href and 'smartstore' not in href and 'brand' not in href and 'shopping' not in href: continue
        if href.endswith('.jpg') or href.endswith('.png'): continue
        # if 'adpost' in str(a.parent.get('class', [])): continue
        
        print(f"  [FALLBACK CANDIDATE] {href}")
        return href
        
    return None

def test_url(url, source, encoding='utf-8'):
    print(f"\nTarget URL: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Referer': 'https://www.google.com/'
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = encoding
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')
        
        content_html = ""
        # Mocking logic from crawler.py
        if source == 'FMKorea':
            target = soup.select_one('.rd_body') or soup.select_one('div.rd_body')
            if target: content_html = str(target)
        elif source == 'Ppomppu':
            target = soup.select_one('table.pic_bg table td.han')
            if not target: target = soup.select_one('.board-contents')
            if target: content_html = str(target)
        
        # Extract
        link = extract_buy_link(soup, source, content_html)
        print(f"Result Link: {link}")
        
        if link:
            name = extract_mall_name_from_url(link)
            print(f"Mall Name: {name}")
        else:
            print("FAILED to extract link.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with URLs from screenshot if possible, or generic recent ones
    print("Test 1: FMKorea")
    test_url("https://www.fmkorea.com/index.php?mid=hotdeal&document_srl=7324883582", "FMKorea") # Example ID, might need actual recent one
    
    print("Test 2: Ppomppu")
    # Using a generic recent hotdeal board link
    # We really need a real link to test effectively. I will try to fetch main list first.
