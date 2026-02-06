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
                    logger.error(f"⚠️ 차단됨 (430) ({url})")
                    return None
                else:
                    logger.warning(f"⚠️ Fetch Failed: {response.status_code} ({url})")
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

    def fetch_content_html(self, url, source):
        """본문 HTML을 가져오는 공통 메소드 - 소스별 로직 분기"""
        try:
            encoding = 'euc-kr' if source == 'Ppomppu' else 'utf-8'
            html = self.fetch_page(url, encoding=encoding)
            if not html: return None, None
            
            soup = BeautifulSoup(html, 'html.parser')
            content_html = ""
            
            if source == 'Ppomppu':
                target = soup.select_one('table.pic_bg table td.han')
                if not target:
                    target = soup.select_one('.board-contents') or soup.find('td', class_='board-contents')
                if target:
                    for tag in target(['script', 'style', 'iframe', 'object']): tag.decompose()
                    content_html = str(target)
                    
            elif source == 'FMKorea':
                target = soup.select_one('.rd_body') or soup.select_one('div.rd_body')
                if target:
                     for tag in target(['script', 'style']): tag.decompose()
                     content_html = str(target)
                     
            elif source == 'Ruliweb':
                target = soup.select_one('.view_content') or soup.select_one('.board_main_view')
                if target:
                     for tag in target(['script', 'style']): tag.decompose()
                     content_html = str(target)

            buy_link = None
            if content_html:
                 content_html = content_html.replace('data-original=', 'src=')
                 
                 # --- Extract Buy Link ---
                 buy_link = self.extract_buy_link(soup, source, content_html)
                 if buy_link:
                     mall_name = self.get_mall_name(buy_link)
                     mall_comment = f"<!-- MALL_NAME: {mall_name} -->" if mall_name else ""
                     content_html = f"<!-- BUY_URL: {buy_link} -->{mall_comment}" + content_html
                     logger.info(f"  -> Extracted Buy Link: {buy_link} ({mall_name})")
                 
                 logger.info(f"  -> Content fetched. Len: {len(content_html)}")
            else:
                 logger.warning(f"  -> Content Extraction Failed. URL: {url} | Src: {source}")
                 content_html = "" 

            return content_html, buy_link # Return both content and extracted link for mall name detection
            
        except Exception as e:
            logger.error(f"  -> Content Fetch Exception ({source}): {e}")
            return "", None

    def extract_mall_name_from_url(self, url):
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

    def extract_buy_link(self, soup, source, content_html):
        """본문에서 쇼핑몰 링크 추출 (강력한 도메인 매칭)"""
        try:
        # ... (rest of extract_buy_link logic is same, but I need to make sure I don't delete it)

            KNOWN_MALLS = [
                'coupang.com', 'coupang.net', 'gmarket.co.kr', 'auction.co.kr', '11st.co.kr', 
                'wemakeprice.com', 'tmon.co.kr', 'ssg.com', 'lotteon.com', 'cjthemarket.com', 
                'aliexpress.com', 'qoo10.com', 'amazon.com', 'smartstore.naver.com', 'brand.naver.com',
                'shopping.naver.com', 'e-himart.co.kr', 'gsshop.com', 'cjmall.com', 'interpark.com',
                'lotimall.com', 'akmall.com', 'hyundaihmall.com', 'shinsegaemall.ssg.com', 'emart.ssg.com'
            ]

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
                        
            # 3. Aggressive Scan: Find ANY link matching Known Malls in content
            c_soup = BeautifulSoup(content_html, 'html.parser')
            links = c_soup.select('a')
            
            # Priority 1: Direct Mall Domains
            for a in links:
                href = a.get('href', '')
                if not href: continue
                # Skip Ads (FMKorea adpost) or Naver Search Ad
                if 'adpost' in str(a.parent.get('class', [])): continue
                if 'adbiz' in href: continue

                for mall in KNOWN_MALLS:
                    if mall in href:
                        return href
            
            # Priority 2: Fallback to first external link if not excluded
            for a in links:
                href = a.get('href', '')
                if not href or href.startswith('#') or href.startswith('javascript'): continue
                if href.startswith('/'): continue # Ignore relative internal links
                if 'ppomppu.co.kr' in href or 'fmkorea.com' in href or 'ruliweb.com' in href: continue
                if 'naver.com' in href and 'smartstore' not in href and 'brand' not in href and 'shopping' not in href: continue
                if href.endswith('.jpg') or href.endswith('.png'): continue
                if 'adpost' in str(a.parent.get('class', [])): continue
                
                return href
        except: pass
        return None

    def extract_mall_name(self, title):
        """제목에서 쇼핑몰 이름 추출 [쇼핑몰] or (쇼핑몰) 패턴"""
        try:
            # [MallName] or (MallName) at start of title
            match = re.search(r'^[\[\(](.+?)[\]\)]', title)
            if match:
                return match.group(1).strip()
        except: pass
        return None

    def save_deal(self, data):
        try:
            data['category'] = self.normalize_category(data.get('category'))
            
            # --- Source Name Refinement ---
            # Reverted: Keep source as 'FMKorea'/'Ppomppu' for icon consistency.
            # Mall name is effectively in the Title.
            # mall_from_title = self.extract_mall_name(data['title'])
            # if mall_from_title:
            #     data['source'] = mall_from_title

            # --- Content Check ---
            if not data.get('content'):
                logger.warning(f"  !! Saving deal with EMPTY content: {data['title'][:15]}...")
            
            # Check if exists by URL
            existing = self.supabase.table("hotdeals").select("id").eq("url", data['url']).execute()
            
            if existing.data and len(existing.data) > 0:
                deal_id = existing.data[0]['id']
                self.supabase.table("hotdeals").update(data).eq("id", deal_id).execute()
            else:
                self.supabase.table("hotdeals").insert(data).execute()
                logger.info(f"  [Insert] {data['source']} | {data['title'][:20]}")

            return True
        except Exception as e:
            logger.error(f"저장 실패: {e}")
        return False

class PpomppuCrawler(BaseCrawler):
    def extract_metadata_from_title(self, title):
        """
        Extracts price and mall name from title pattern: [Mall] Product (Price / Delivery)
        Returns: (price, mall_name)
        """
        price = "가격미상"
        
        # Extract Price inside parentheses: (10,000원 / 무배)
        # Match number with comma ending with 원 or just number, or 무료
        p_match = re.search(r'\(([^)]+)\)', title)
        if p_match:
            inner = p_match.group(1)
            # Find price-like pattern in the inner text
            price_match = re.search(r'([\d,]+원?|무료)', inner)
            if price_match:
                price = price_match.group(1)
        
        return price

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
                
                content_html, buy_link = self.fetch_content_html(link, 'Ppomppu')
                
                img_url = ""
                thumb_link = item.select_one('.baseList-thumb')
                if thumb_link and thumb_link.has_attr('tooltip') and 'P_img:' in thumb_link['tooltip']:
                    img_url = thumb_link['tooltip'].split('P_img:')[-1]
                if not img_url:
                    img_el = item.select_one('.baseList-thumb img')
                    if img_el and 'src' in img_el.attrs: img_url = img_el['src']
                if img_url.startswith('//'): img_url = "https:" + img_url
                
                full_title = title_el.get_text().strip()
                price = self.extract_metadata_from_title(full_title)
                
                cat_el = item.select_one('.baseList-small') 
                category = cat_el.get_text().replace('[', '').replace(']', '').strip() if cat_el else "기타"
                comm_el = item.select_one('.baseList-c'); comment = int(comm_el.get_text().strip()) if comm_el else 0
                like_el = item.select_one('.baseList-rec'); like = int(re.findall(r'\d+', like_el.get_text())[0]) if like_el and re.findall(r'\d+', like_el.get_text()) else 0
                
                source_name = "Ppomppu" # Will be updated by title extraction in save_deal or buy_link
                if buy_link:
                    detected_mall = self.extract_mall_name_from_url(buy_link)
                    if detected_mall: source_name = detected_mall

                if self.save_deal({
                    "title": full_title, 
                    "url": link, 
                    "img_url": img_url, 
                    "source": source_name, 
                    "category": category, 
                    "price": price, 
                    "comment_count": comment, 
                    "like_count": like,
                    "content": content_html
                }): count += 1
                time.sleep(1.0)
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
                content_html = None
                buy_link = None
                price = "가격미상"
                
                # Fetch Detail Page
                try:
                    time.sleep(1.0 + random.random() * 1.0) 
                    d_html = self.fetch_page(link)
                    if d_html:
                        d_soup = BeautifulSoup(d_html, 'html.parser')
                        
                        # FMKorea Specific Information Section
                        # Usually in a div with class 'hotdeal_info' or similar table structure
                        info_div = d_soup.select_one('.hotdeal_info')
                        if info_div:
                            # Extract price
                            p_txt = info_div.get_text()
                            p_match = re.search(r'가격\s*:\s*([0-9,]+원?)', p_txt)
                            if p_match: price = p_match.group(1)
                            
                            # Extract Link from the info section
                            link_a = info_div.select_one('a')
                            if link_a and link_a.has_attr('href'):
                                buy_link = link_a['href']

                        # Image
                        img_el = d_soup.select_one('article img')
                        if img_el: img_url = img_el.get('src') or img_el.get('data-original') or ""
                        
                        # Content
                        target = d_soup.select_one('.rd_body') or d_soup.select_one('div.rd_body')
                        if target:
                             for tag in target(['script', 'style']): tag.decompose()
                             content_html = str(target).replace('data-original=', 'src=')
                             
                             # If buy_link was not found in info_div, try base extractor
                             if not buy_link:
                                 buy_link = self.extract_buy_link(d_soup, 'FMKorea', content_html)
                                 
                             if buy_link:
                                 content_html = f"<!-- BUY_URL: {buy_link} -->" + content_html
                except: pass

                if not img_url:
                    t_el = item.select_one('img.thumb')
                    if t_el: img_url = (t_el.get('data-original') or t_el.get('src') or "").replace('70x50', '140x100')
                if img_url.startswith('//'): img_url = "https:" + img_url
                
                # List view fallback price
                if price == "가격미상":
                     info_div = item.select_one('.hotdeal_info')
                     if info_div:
                        p_m = re.search(r'가격:\s*([0-9,]+원)', info_div.get_text())
                        if p_m: price = p_m.group(1)

                cat_el = item.select_one('.category a'); category = cat_el.get_text().strip() if cat_el else "기타"
                comm_span = title_el.select_one('.comment_count'); comment = int(comm_span.get_text().strip('[] ')) if comm_span and comm_span.get_text().strip('[] ').isdigit() else 0
                v_el = item.select_one('.pc_voted_count .count'); like = int(v_el.get_text().strip()) if v_el and v_el.get_text().strip().isdigit() else 0
                
                source_name = "FMKorea"
                if buy_link:
                    detected_mall = self.extract_mall_name_from_url(buy_link)
                    if detected_mall: source_name = detected_mall

                if self.save_deal({
                    "title": title, 
                    "url": link, 
                    "img_url": img_url, 
                    "source": source_name, 
                    "category": category, 
                    "price": price, 
                    "comment_count": comment, 
                    "like_count": like,
                    "content": content_html
                }): count += 1
                time.sleep(0.05)
            except Exception as e: logger.error(f"FMKorea 에러: {e}")
        logger.info(f"=== [FMKorea] 크롤링 완료 ({count}건) ===")

class RuliwebCrawler(BaseCrawler):
    def crawl(self):
        logger.info("=== [Ruliweb] 크롤링 시작 ===")
        url = "https://bbs.ruliweb.com/market/board/1020?view=gallery"
        html = self.fetch_page(url)
        if not html: return
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select('div.flex_item.article_wrapper')
        if not items:
            items = soup.select('table.board_list_table tr.table_body:not(.notice)')
        count = 0
        for item in items:
            try:
                # Common variable initialization
                link = ""; title = ""; img_url = ""; 
                like = 0; comment = 0; cat = "기타"

                if item.name == 'div': 
                    subject_div = item.select_one('.subject_wrapper')
                    if not subject_div: continue
                    t_el = subject_div.select_one('a.subject_link')
                    link = t_el['href'] if t_el else ""
                    title = t_el.get_text().strip() if t_el else ""
                    thumb_a = item.select_one('a.thumbnail')
                    if thumb_a and thumb_a.has_attr('style'):
                        urls = re.findall(r'url\((.*?)\)', thumb_a['style'])
                        if urls: img_url = urls[0].strip("'\"")
                    rec_el = item.select_one('.recomd')
                    if rec_el: 
                        nums = re.findall(r'\d+', rec_el.get_text())
                        if nums: like = int(nums[0])
                    com_el = subject_div.select_one('.num_reply .num') if subject_div else None
                    if com_el:
                         nums = re.findall(r'\d+', com_el.get_text())
                         if nums: comment = int(nums[0])
                    cat = self.normalize_category(title)
                else: 
                    t_el = item.select_one('a.subject_link')
                    if not t_el: continue
                    title = t_el.get_text().strip(); link = t_el.get('href', '')
                    cat_el = item.select_one('.category') or item.select_one('.divsn')
                    cat = self.normalize_category(cat_el.get_text()) if cat_el else "기타"
                    c_el = item.select_one('.num_reply') or item.select_one('.num_comment')
                    if c_el:
                        nums = re.findall(r'\d+', c_el.get_text())
                        if nums: comment = int(nums[0])
                    l_el = item.select_one('.recomd')
                    if l_el:
                        nums = re.findall(r'\d+', l_el.get_text())
                        if nums: like = int(nums[0])

                if not link: continue
                if link.startswith('/'): link = "https://bbs.ruliweb.com" + link
                if img_url.startswith('//'): img_url = "https:" + img_url
                if img_url and not img_url.startswith('http'): img_url = "https://bbs.ruliweb.com" + img_url
                
                price = "가격미상"
                p_match = re.search(r'[\[\(]\s*([\d,]+(?:원)?|무료)\s*(?:/|\]|\))', title)
                if p_match: price = p_match.group(1)
                else:
                    p_match2 = re.search(r'([\d,]+원)', title)
                    if p_match2: price = p_match2.group(1)

                content_html, buy_link = self.fetch_content_html(link, 'Ruliweb')
                
                source_name = "Ruliweb"
                if buy_link:
                    detected_mall = self.extract_mall_name_from_url(buy_link)
                    if detected_mall: source_name = detected_mall

                if self.save_deal({
                    "title": title, 
                    "url": link, 
                    "img_url": img_url, 
                    "source": source_name, 
                    "category": cat, 
                    "price": price, 
                    "comment_count": comment, 
                    "like_count": like,
                    "content": content_html
                }): count += 1
                time.sleep(1.0) 
            except Exception as e: logger.error(f"Ruliweb 에러: {e}")
        logger.info(f"=== [Ruliweb] 크롤링 완료 ({count}건) ===")

def main():
    p = PpomppuCrawler(URL, KEY); f = FMKoreaCrawler(URL, KEY); r = RuliwebCrawler(URL, KEY)
    p.crawl(); f.crawl(); r.crawl()

if __name__ == "__main__":
    main()