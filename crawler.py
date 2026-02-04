import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import time
import re
import sys
import io
import logging

# 터미널 출력 및 로깅 인코딩 강제 설정 (Windows mojibake 방지)
if sys.stdout.encoding != 'utf-8':
    try:
        # sys.stdout.reconfigure는 Python 3.7+에서 지원
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        else:
            # 하위 버전 호환성
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
    
    # 터미널 출력용 핸들러 (UTF-8 강제)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(stream_handler)
    
    # 파일 저장용 핸들러 (UTF-8 강제)
    file_handler = logging.FileHandler("crawler.log", encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(file_handler)

import random

class BaseCrawler:
    def __init__(self, supabase_url, supabase_key):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/121.0.0.0'
        ]

    def fetch_page(self, url, encoding='utf-8', retries=3):
        for i in range(retries):
            try:
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
                
                if 'fmkorea' in url:
                    headers.update({'Referer': 'https://www.google.com/'})

                response = requests.get(url, headers=headers, timeout=12)
                
                if response.status_code == 200:
                    try:
                        return response.content.decode(encoding, errors='replace')
                    except LookupError:
                        return response.content.decode('utf-8', errors='replace')
                elif response.status_code == 430:
                    logger.error(f"⚠️ FMKorea 차단됨 (430). 사이트에서 로봇 접속을 제한하고 있습니다. 잠시(약 30분) 후 시도하세요.")
                    return None
                        
                logger.warning(f"[{i+1}/{retries}] 페이지 로딩 실패: {response.status_code} ({url})")
            except Exception as e:
                logger.error(f"[{i+1}/{retries}] 네트워크 에러: {e}")
            
            if i < retries - 1:
                time.sleep((i + 1) * 3)
        return None
    
    def normalize_category(self, raw_cat):
        if not raw_cat: return "기타"
        cat = raw_cat.strip()
        if cat in ["PC제품", "컴퓨터", "노트북", "PC부품", "모니터"]: return "컴퓨터"
        if cat in ["디지털", "모바일", "상품권", "모바일/상품권", "SW/게임"]: return "디지털"
        if cat in ["식품/건강", "먹거리", "식품", "건강", "생활/식품"]: return "식품/건강"
        if cat in ["가전/가구", "가전제품", "가전", "가구", "인테리어"]: return "가전/가구"
        if cat in ["의류/잡화", "의류", "패션", "뷰티", "잡화"]: return "의류/잡화"
        if "컴퓨터" in cat: return "컴퓨터"
        if "디지털" in cat: return "디지털"
        if "식품" in cat or "건강" in cat: return "식품/건강"
        if "가전" in cat or "가구" in cat: return "가전/가구"
        if "의류" in cat or "잡화" in cat: return "의류/잡화"
        return "기타"

    def save_deal(self, data):
        try:
            data['category'] = self.normalize_category(data.get('category'))
            self.supabase.table("hotdeals").upsert(data).execute()
            logger.info(f"[{data['source']}] {data['category']} | {data['title'][:20]} | {data['price']}")
            return True
        except Exception as e:
            if '23505' in str(e) or 'duplicate key' in str(e):
                try:
                    self.supabase.table("hotdeals").update(data).eq("url", data['url']).execute()
                    logger.info(f"[{data['source']}] {data['category']} (UP) | {data['title'][:20]}... | {data['price']}")
                    return True
                except Exception as update_error:
                    logger.error(f"업데이트 실패: {update_error}")
            else:
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
                title_el = item.select_one('.baseList-title')
                if not title_el: continue
                full_title = title_el.get_text().strip()
                href = title_el['href']
                link = ("https://www.ppomppu.co.kr" + href) if href.startswith('/') else ("https://www.ppomppu.co.kr/zboard/" + href)
                img_url = ""
                thumb_link = item.select_one('.baseList-thumb')
                if thumb_link and thumb_link.has_attr('tooltip') and 'P_img:' in thumb_link['tooltip']:
                    img_url = thumb_link['tooltip'].split('P_img:')[-1]
                if not img_url:
                    img_el = item.select_one('.baseList-thumb img')
                    if img_el and 'src' in img_el.attrs: img_url = img_el['src']
                if img_url:
                    if img_url.startswith('//'): img_url = "https:" + img_url
                    elif not img_url.startswith('http'): img_url = "https://www.ppomppu.co.kr" + img_url
                price = self.extract_price(full_title)
                category = "기타"
                cat_el = item.select_one('.baseList-small') 
                if cat_el:
                    raw_cat = cat_el.get_text().strip()
                    category = raw_cat.replace('[', '').replace(']', '').strip()
                comment_el = item.select_one('.baseList-c')
                comment_count = int(comment_el.get_text().strip()) if comment_el else 0
                
                # 추천수 추출
                like_count = 0
                like_el = item.select_one('.baseList-rec')
                if like_el:
                    try:
                        like_text = like_el.get_text().strip()
                        if like_text:
                            # "추천: X" 또는 숫자만 있는 경우 대응
                            numbers = re.findall(r'\d+', like_text)
                            if numbers: like_count = int(numbers[0])
                    except: pass

                data = {
                    "title": full_title, 
                    "url": link, 
                    "img_url": img_url, 
                    "source": "Ppomppu", 
                    "category": category, 
                    "price": price, 
                    "comment_count": comment_count,
                    "like_count": like_count
                }
                if self.save_deal(data): count += 1
                time.sleep(0.05)
            except Exception as e: logger.error(f"Ppomppu 항목 에러: {e}")
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
                target_span = title_el.select_one('.ellipsis-target')
                title = target_span.get_text().strip() if target_span else title_el.get_text().strip()
                href = title_el['href']
                link = ("https://www.fmkorea.com" + href) if href.startswith('/') else href
                
                # 안정성을 위해 상세 페이지 방문은 제외 (430 에러 방지)
                img_url = ""
                thumb_el = item.select_one('img.thumb')
                if thumb_el:
                    img_url = thumb_el.get('data-original') or thumb_el.get('src') or ""
                if img_url:
                    if img_url.startswith('//'): 
                        img_url = "https:" + img_url
                    # 저해상도(70x50)를 고해상도(140x100)로 변경
                    img_url = img_url.replace('70x50', '140x100')

                info_div = item.select_one('.hotdeal_info')
                price = "가격미상"
                if info_div:
                    info_text = info_div.get_text()
                    price_match = re.search(r'가격:\s*([0-9,]+원)', info_text)
                    if price_match: price = price_match.group(1)
                    else:
                        strongs = info_div.select('a.strong')
                        if len(strongs) >= 2: price = strongs[1].get_text().strip()
                category = "기타"
                cat_el = item.select_one('.category a')
                if cat_el: category = cat_el.get_text().strip()
                comment_count = 0
                comment_span = title_el.select_one('.comment_count')
                if comment_span:
                    c_text = comment_span.get_text().strip('[] ')
                    if c_text.isdigit(): comment_count = int(c_text)
                
                # 추천수 추출 (FMKorea는 info div에 '추천' 텍스트로 있을 확률 높음)
                like_count = 0
                if info_div:
                    info_text = info_div.get_text()
                    # "추천: 10" 형태 검색
                    like_match = re.search(r'추천[:\s]*(\d+)', info_text)
                    if like_match:
                        like_count = int(like_match.group(1))
                
                data = {
                    "title": title, 
                    "url": link, 
                    "img_url": img_url, 
                    "source": "FMKorea", 
                    "category": category, 
                    "price": price, 
                    "comment_count": comment_count,
                    "like_count": like_count
                }
                if self.save_deal(data): count += 1
                time.sleep(1.0) # FMKorea는 차단 방지를 위해 더 긴 딜레이 적용
            except Exception as e: logger.error(f"FMKorea 항목 에러: {e}")
        logger.info(f"=== [FMKorea] 크롤링 완료 ({count}건) ===")

def main():
    ppomppu = PpomppuCrawler(URL, KEY)
    fmkorea = FMKoreaCrawler(URL, KEY)
    ppomppu.crawl()
    fmkorea.crawl()

if __name__ == "__main__":
    main()