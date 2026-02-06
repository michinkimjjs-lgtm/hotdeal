import requests
from bs4 import BeautifulSoup
import re
import logging
import sys

# Logger setup
logger = logging.getLogger("debug_content")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(handler)

def fetch_page(url, encoding='utf-8'):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.content.decode(encoding, errors='replace')
        else:
            logger.error(f"Status Code: {res.status_code}")
            return None
    except Exception as e:
        logger.error(f"Fetch Error: {e}")
        return None

def test_ppomppu():
    logger.info("--- Testing Ppomppu Content ---")
    # Ppomppu List to get a URL
    list_url = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
    html = fetch_page(list_url, 'euc-kr')
    if not html: return
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find first non-notice post
    item = soup.select_one('tr.baseList:not(.baseNotice) .baseList-title')
    if not item: 
        logger.info("No item found.")
        return

    link = "https://www.ppomppu.co.kr/zboard/" + item['href']
    logger.info(f"Target URL: {link}")
    
    # Fetch Content
    detail_html = fetch_page(link, 'euc-kr')
    if not detail_html: return
    d_soup = BeautifulSoup(detail_html, 'html.parser')
    
    target = d_soup.select_one('.board-contents') or d_soup.find('td', class_='board-contents')
    if target:
        content = str(target)[:100] + "..."
        logger.info(f"✅ Content Found! Length: {len(str(target))}")
        logger.info(f"Sample: {content}")
    else:
        logger.error("❌ Content NOT Found with selector .board-contents or td.board-contents")

def test_fmkorea():
    logger.info("\n--- Testing FMKorea Content ---")
    list_url = "https://www.fmkorea.com/hotdeal"
    html = fetch_page(list_url)
    if not html: return
    soup = BeautifulSoup(html, 'html.parser')
    
    item = soup.select_one('.fm_best_widget._bd_pc li.li h3.title a.hotdeal_var8')
    if not item:
        item = soup.select_one('.bd_lst_wrp .bd_lst tr:not(.notice) h3.title a')
        
    if not item:
        logger.info("No item found.")
        return

    link = "https://www.fmkorea.com" + item['href']
    logger.info(f"Target URL: {link}")
    
    detail_html = fetch_page(link)
    if not detail_html: return
    d_soup = BeautifulSoup(detail_html, 'html.parser')
    
    target = d_soup.select_one('.rd_body') or d_soup.select_one('div.rd_body')
    if target:
        content = str(target)[:100] + "..."
        logger.info(f"✅ Content Found! Length: {len(str(target))}")
        logger.info(f"Sample: {content}")
    else:
        logger.error("❌ Content NOT Found .rd_body")

def test_ruliweb():
    logger.info("\n--- Testing Ruliweb Content ---")
    list_url = "https://bbs.ruliweb.com/market/board/1020?view=gallery"
    html = fetch_page(list_url)
    if not html: return
    soup = BeautifulSoup(html, 'html.parser')
    
    # Try gallery item
    item = soup.select_one('div.flex_item.article_wrapper a.subject_link')
    if not item:
        # Try list item
        item = soup.select_one('table.board_list_table tr.table_body .subject_link')

    if not item:
        logger.info("No item found.")
        return

    link = item['href']
    if link.startswith('/'): link = "https://bbs.ruliweb.com" + link
    logger.info(f"Target URL: {link}")
    
    detail_html = fetch_page(link)
    if not detail_html: return
    d_soup = BeautifulSoup(detail_html, 'html.parser')
    
    target = d_soup.select_one('.view_content') or d_soup.select_one('.board_main_view')
    if target:
        content = str(target)[:100] + "..."
        logger.info(f"✅ Content Found! Length: {len(str(target))}")
        logger.info(f"Sample: {content}")
    else:
        logger.error("❌ Content NOT Found .view_content")

if __name__ == "__main__":
    test_ppomppu()
    test_fmkorea()
    test_ruliweb()
