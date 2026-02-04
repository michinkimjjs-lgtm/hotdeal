import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import time
import random
import re
import sys
import io
import logging

# 터미널 출력 및 로깅 인코딩 강제 설정 (Windows mojibake 방지)
if sys.stdout.encoding != 'utf-8':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        else:
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except Exception:
        pass

# Supabase 설정
URL: str = "https://zvlntvovzffizoruwxqx.supabase.co"
KEY: str = "sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV"

# 로깅 설정
logger = logging.getLogger("crawler")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(stream_handler)
    file_handler = logging.FileHandler("crawler.log", encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(file_handler)

class BaseCrawler:
    def __init__(self, supabase_url, supabase_key):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ]

    def fetch_page(self, url, encoding='utf-8', retries=3):
        for i in range(retries):
            try:
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Referer': 'https://www.google.com/'
                }
                response = self.session.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    try:
                        return response.content.decode(encoding, errors='replace')
                    except LookupError:
                        return response.content.decode('utf-8', errors='replace')
                elif response.status_code == 430:
                    logger.error(f"⚠️ 차단됨 (430) ({url})")
                    return None
            except Exception as e:
                logger.error(f"에러: {e}")
            if i < retries - 1:
                time.sleep((i + 1) * 3 + random.random() * 2)
        return None
    
    def normalize_category(self, raw_cat):
        if not raw_cat: return "기타"
        cat = raw_cat.strip()
        if any(x in cat for x in ["PC", "컴퓨터", "노트북", "PC부품", "모니터"]): return "컴퓨터"
        if any(x in cat for x in ["디지털", "모바일", "상품권", "SW", "게임"]): return "디지털"
        if any(x in cat for x in ["식품", "건강", "먹거리"]): return "식품/건강"
        if any(x in cat for x in ["가전", "가구", "인테리어"]): return "가전/가구"
        if any(x in cat for x in ["의류", "패션", "뷰티", "잡화"]): return "의류/잡화"
        return "기타"

    def save_deal(self, data):
        try:
            data['category'] = self.normalize_category(data.get('category'))
            self.supabase.table("hotdeals").upsert(data).execute()
            logger.info(f"[{data['source']}] {data['category']} | {data['title'][:20]} | {data['price']}")
            return True
        except Exception as e:
            logger.error(f"저장 실패: {e}")
        return False

class PpomppuCrawler(BaseCrawler):
    def extract_price(self, title):
        try:
            match = re.search(r'[\(\[]\s*([\d,]+(?:원|만원|원)?)\s*(?:/|\]|\))', title)
            if match: return match.group(1).strip()
            match_won = re.search(r'([\d,]+(?:원|만원))', title)
            if match_won: return match_won.group(1).strip()
        except: pass
        return "가격미상"

    def crawl(self):
        logger.info("=== [Ppomppu] 크롤링 시작 ===")
        url = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
        html = self.fetch_page(url, encoding='euc-kr')
        if not html: return
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select('tr.baseList')
        count = 0
        for item in items:
            try:
                if 'baseNotice' in item.get('class', []): continue
                title_el = item.select_one('.baseList-title'); href = title_el['href'] if title_el else ""
                if not title_el: continue
                link = ("https://www.ppomppu.co.kr" + href) if href.startswith('/') else ("https://www.ppomppu.co.kr/zboard/" + href)
                img_url = ""
                thumb_link = item.select_one('.baseList-thumb')
                if thumb_link and thumb_link.has_attr('tooltip') and 'P_img:' in thumb_link['tooltip']:
                    img_url = thumb_link['tooltip'].split('P_img:')[-1]
                if not img_url:
                    img_el = item.select_one('.baseList-thumb img')
                    if img_el and 'src' in img_el.attrs: img_url = img_el['src']
                if img_url.startswith('//'): img_url = "https:" + img_url
                price = self.extract_price(title_el.get_text().strip())
                cat_el = item.select_one('.baseList-small') 
                category = cat_el.get_text().replace('[', '').replace(']', '').strip() if cat_el else "기타"
                comm_el = item.select_one('.baseList-c'); comment = int(comm_el.get_text().strip()) if comm_el else 0
                like_el = item.select_one('.baseList-rec'); like = int(re.findall(r'\d+', like_el.get_text())[0]) if like_el and re.findall(r'\d+', like_el.get_text()) else 0
                if self.save_deal({"title": title_el.get_text().strip(), "url": link, "img_url": img_url, "source": "Ppomppu", "category": category, "price": price, "comment_count": comment, "like_count": like}): count += 1
                time.sleep(0.05)
            except Exception as e: logger.error(f"Ppomppu 에러: {e}")
        logger.info(f"=== [Ppomppu] 크롤링 완료 ({count}건) ===")

class FMKoreaCrawler(BaseCrawler):
    def crawl(self):
        logger.info("=== [FMKorea] 크롤링 시작 ===")
        url = "https://www.fmkorea.com/hotdeal"
        html = self.fetch_page(url)
        if not html: return
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select('.fm_best_widget._bd_pc li.li')
        if not items: items = soup.select('.bd_lst_wrp .bd_lst tr:not(.notice)')
        count = 0
        for item in items:
            try:
                title_el = item.select_one('h3.title a.hotdeal_var8')
                if not title_el: continue
                title = title_el.get_text().strip(); link = ("https://www.fmkorea.com" + title_el['href']) if title_el['href'].startswith('/') else title_el['href']
                img_url = ""
                if not getattr(self, 'is_details_blocked', False):
                    try:
                        time.sleep(1.0 + random.random() * 1.0) # 속도 개선: 3-5초 -> 1-2초
                        d_html = self.fetch_page(link); d_soup = BeautifulSoup(d_html, 'html.parser') if d_html else None
                        if d_soup:
                            img_el = d_soup.select_one('article img'); img_url = img_el.get('src') or img_el.get('data-original') or ""
                        else: self.is_details_blocked = True
                    except: pass
                if not img_url:
                    t_el = item.select_one('img.thumb')
                    if t_el: img_url = (t_el.get('data-original') or t_el.get('src') or "").replace('70x50', '140x100')
                if img_url.startswith('//'): img_url = "https:" + img_url
                info_div = item.select_one('.hotdeal_info'); price = "가격미상"
                if info_div:
                    p_m = re.search(r'가격:\s*([0-9,]+원)', info_div.get_text())
                    if p_m: price = p_m.group(1)
                cat_el = item.select_one('.category a'); category = cat_el.get_text().strip() if cat_el else "기타"
                comm_span = title_el.select_one('.comment_count'); comment = int(comm_span.get_text().strip('[] ')) if comm_span and comm_span.get_text().strip('[] ').isdigit() else 0
                v_el = item.select_one('.pc_voted_count .count'); like = int(v_el.get_text().strip()) if v_el and v_el.get_text().strip().isdigit() else 0
                if self.save_deal({"title": title, "url": link, "img_url": img_url, "source": "FMKorea", "category": category, "price": price, "comment_count": comment, "like_count": like}): count += 1
                time.sleep(0.1) # 항목 간 대기 시간 단축
            except Exception as e: logger.error(f"FMKorea 에러: {e}")
        logger.info(f"=== [FMKorea] 크롤링 완료 ({count}건) ===")

class RuliwebCrawler(BaseCrawler):
    def crawl(self):
        logger.info("=== [Ruliweb] 크롤링 시작 ===")
        url = "https://bbs.ruliweb.com/market/board/1020"
        html = self.fetch_page(url)
        if not html: return
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select('tr.list_table_row:not(.notice)')
        count = 0
        for item in items:
            try:
                t_el = item.select_one('a.subject_link')
                if not t_el: continue
                title = t_el.get_text().strip(); link = ("https://bbs.ruliweb.com" + t_el['href']) if t_el['href'].startswith('/') else t_el['href']
                img_el = item.select_one('img.thumb'); img_url = img_el.get('src') or img_el.get('data-src') or ""
                if img_url.startswith('//'): img_url = "https:" + img_url
                price = "가격미상"; p_m = re.search(r'([0-9,]+원)', title)
                if p_m: price = p_m.group(1)
                rec = item.select_one('.recomd_count .count') or item.select_one('.recomm'); like = int(rec.get_text()) if rec and rec.get_text().strip().isdigit() else 0
                com = item.select_one('.num_comment .num') or item.select_one('.num_comment'); comment = int(com.get_text().strip('[]() ')) if com and com.get_text().strip('[]() ').isdigit() else 0
                cat_el = item.select_one('.category'); category = self.normalize_category(cat_el.get_text()) if cat_el else "기타"
                if self.save_deal({"title": title, "url": link, "img_url": img_url, "source": "Ruliweb", "category": category, "price": price, "comment_count": comment, "like_count": like}): count += 1
                time.sleep(0.2)
            except Exception as e: logger.error(f"Ruliweb 에러: {e}")
        logger.info(f"=== [Ruliweb] 크롤링 완료 ({count}건) ===")

def main():
    p = PpomppuCrawler(URL, KEY); f = FMKoreaCrawler(URL, KEY); r = RuliwebCrawler(URL, KEY)
    p.crawl(); f.crawl(); r.crawl()

if __name__ == "__main__":
    main()