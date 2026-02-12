import requests
from bs4 import BeautifulSoup
import re
import sys
import io

# 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def extract_mall_name_from_url(url):
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

def fetch_content_html(url):
    print(f"Fetching Content: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        res = requests.get(url, headers=headers)
        res.encoding = 'euc-kr' # 뽐뿌는 EUC-KR
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')
        
        # 1. 본문 추출
        target = soup.select_one('table.pic_bg table td.han')
        if not target:
            target = soup.select_one('.board-contents')
        
        content_html = ""
        if target:
            for tag in target(['script', 'style', 'iframe', 'object']): tag.decompose()
            content_html = str(target)
            
        # 2. 구매 링크 추출 (기존 로직 + 강화)
        buy_link = None
        
        # Method A: wordfix (Legacy)
        wordfix = soup.select_one('.wordfix')
        if wordfix:
            for a in wordfix.select('a'):
                if a.has_attr('href'): 
                    buy_link = a['href']
                    break
        
        # Method B: scrap_bx (New)
        if not buy_link:
            scrap_links = soup.select('a.scrap_bx_href')
            for a in scrap_links:
                if a.has_attr('href'): 
                    buy_link = a['href']
                    break

        # Method C: 본문 내 링크 검색
        if not buy_link:
            links = soup.select('table.pic_bg table td.han a')
            for a in links:
                href = a.get('href','')
                if 'ppomppu.co.kr' not in href and href.startswith('http'):
                     buy_link = href
                     break
        
        # Ppomppu Redirect Resolution (s.ppomppu.co.kr)
        if buy_link and 's.ppomppu.co.kr' in buy_link:
            import base64
            from urllib.parse import parse_qs, urlparse, unquote
            try:
                parsed = urlparse(buy_link)
                qs = parse_qs(parsed.query)
                if 'target' in qs:
                    target_b64 = qs['target'][0]
                    # Fix padding if necessary
                    missing_padding = len(target_b64) % 4
                    if missing_padding:
                        target_b64 += '=' * (4 - missing_padding)
                    decoded_url = base64.b64decode(target_b64).decode('utf-8')
                    buy_link = decoded_url
            except Exception as e:
                print(f"Redirect resolution failed: {e}")

        return content_html, buy_link, soup

    except Exception as e:
        print(f"Error fetching content: {e}")
        return "", None, None

def debug_ppomppu():
    print("=== Ppomppu Single Item Debug ===")
    url = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    
    res = requests.get(url, headers=headers)
    res.encoding = 'euc-kr'
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # 첫 번째 게시글 찾기
    items = soup.select('tr.baseList')
    target_item = None
    
    for item in items:
        if 'baseNotice' in item.get('class', []): continue
        target_item = item
        break
        
    if not target_item:
        print("No items found.")
        return

    # 데이터 추출
    title_el = target_item.select_one('.baseList-title')
    title = title_el.get_text().strip()
    href = title_el['href']
    link = ("https://www.ppomppu.co.kr" + href) if href.startswith('/') else ("https://www.ppomppu.co.kr/zboard/" + href)
    
    print(f"\n[Target Item]")
    print(f"Title: {title}")
    print(f"Link: {link}")
    
    # 상세 페이지 크롤링
    content, buy_link, d_soup = fetch_content_html(link)
    
    print(f"\n[Extracted Data]")
    print(f"Buy Link (Resolved): {buy_link}")
    
    mall_name = extract_mall_name_from_url(buy_link)
    print(f"Mall Name: {mall_name}")
    
    # 이미지 태그 검사
    if d_soup:
        imgs = d_soup.select('table.pic_bg table td.han img')
        for img in imgs:
            print(f"Image Tag: {img}")

if __name__ == "__main__":
    debug_ppomppu()
