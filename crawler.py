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
            # (12,345 / 무료) or [12,345] patterns
            match = re.search(r'[\[\(]\s*([\d,]+(?:원)?|무료)\s*(?:/|\]|\))', title)
            if match: return match.group(1).strip()
            # 10,000원 pattern
            match_won = re.search(r'([\d,]+원)', title)
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
                time.sleep(0.05) # 성능 최적화: 대기 시간 최소화
            except Exception as e: logger.error(f"FMKorea 에러: {e}")
        logger.info(f"=== [FMKorea] 크롤링 완료 ({count}건) ===")

class RuliwebCrawler(BaseCrawler):
    def crawl(self):
        logger.info("=== [Ruliweb] 크롤링 시작 ===")
        # 갤러리 뷰로 요청하여 썸네일 노출 유도
        url = "https://bbs.ruliweb.com/market/board/1020?view=gallery"
        html = self.fetch_page(url)
        if not html: return
        soup = BeautifulSoup(html, 'html.parser')

        # 갤러리 뷰 아이템 선택자
        items = soup.select('div.flex_item.article_wrapper')
        if not items:
            # Fallback to list view selector if gallery view fails
            items = soup.select('table.board_list_table tr.table_body:not(.notice)')
            
        count = 0
        for item in items:
            try:
                # 갤러리 뷰 구조 파싱
                if item.name == 'div':
                    subject_div = item.select_one('.subject_wrapper')
                    if not subject_div: continue
                    t_el = subject_div.select_one('a.subject_link')
                    link = t_el['href'] if t_el else ""
                    title = t_el.get_text().strip() if t_el else ""
                    
                    # 썸네일 추출 (background-image 파싱)
                    img_url = ""
                    thumb_a = item.select_one('a.thumbnail')
                    if thumb_a and thumb_a.has_attr('style'):
                        style = thumb_a['style']
                        # background-image: url(...), url(...) 
                        # 보통 첫 번째 url이 썸네일 (AVIF 또는 WEBP)
                        urls = re.findall(r'url\((.*?)\)', style)
                        if urls:
                            img_url = urls[0].strip("'\"")
                    
                    # 수치 정보
                    like = 0
                    rec_el = item.select_one('.recomd')
                    if rec_el:
                         # 텍스트 내에서 숫자만 추출
                         txt = rec_el.get_text().strip()
                         nums = re.findall(r'\d+', txt)
                         if nums: like = int(nums[0])
                    
                    comment = 0
                    com_el = subject_div.select_one('.num_reply .num') if subject_div else None
                    if com_el:
                         # (10) 형태
                         c_txt = com_el.get_text().strip()
                         nums = re.findall(r'\d+', c_txt)
                         if nums: comment = int(nums[0])

                    cat = "기타" # 갤러리 뷰에서는 카테고리가 명시적으로 안 보일 수 있음. 
                               # 제목 앞 말머리가 있다면 그것을 사용.
                    # Fallback category logic based on title keywords
                    cat = self.normalize_category(title)

                else:
                    # 리스트 뷰 구조 파싱 (기존 로직 유지)
                    t_el = item.select_one('a.subject_link')
                    if not t_el: continue
                    title = t_el.get_text().strip(); link = t_el.get('href', '')
                    
                    img_url = ""
                    # 리스트 뷰에서는 썸네일 찾기 어려움
                    
                    cat_el = item.select_one('.category') or item.select_one('.divsn')
                    cat = self.normalize_category(cat_el.get_text()) if cat_el else "기타"
                    
                    comment = 0
                    c_el = item.select_one('.num_reply') or item.select_one('.num_comment')
                    if c_el:
                        nums = re.findall(r'\d+', c_el.get_text())
                        if nums: comment = int(nums[0])
                        
                    like = 0
                    l_el = item.select_one('.recomd')
                    if l_el:
                        nums = re.findall(r'\d+', l_el.get_text())
                        if nums: like = int(nums[0])

                if not link: continue
                if link.startswith('/'): link = "https://bbs.ruliweb.com" + link
                
                # 프로토콜 보정
                if img_url.startswith('//'): img_url = "https:" + img_url
                if img_url and not img_url.startswith('http'): img_url = "https://bbs.ruliweb.com" + img_url
                
                # 가격 파싱 개선
                price = "가격미상"
                # 뽐뿌/루리웹 공통 정규식: (12,345원) (무료) (1,000 / 무료) 등
                # 1. 괄호 안의 숫자+원 또는 무료 찾기
                # 루리웹: [12,345원] 등
                p_match = re.search(r'[\[\(]\s*([\d,]+(?:원)?|무료)\s*(?:/|\]|\))', title)
                if p_match:
                    price = p_match.group(1)
                else:
                    # 그냥 숫자+원 패턴 찾기
                    p_match2 = re.search(r'([\d,]+원)', title)
                    if p_match2: price = p_match2.group(1)

                if self.save_deal({"title": title, "url": link, "img_url": img_url, "source": "Ruliweb", "category": cat, "price": price, "comment_count": comment, "like_count": like}): count += 1
                time.sleep(0.05)
            except Exception as e: logger.error(f"Ruliweb 에러: {e}")
        logger.info(f"=== [Ruliweb] 크롤링 완료 ({count}건) ===")

def main():
    p = PpomppuCrawler(URL, KEY); f = FMKoreaCrawler(URL, KEY); r = RuliwebCrawler(URL, KEY)
    p.crawl(); f.crawl(); r.crawl()

if __name__ == "__main__":
    main()