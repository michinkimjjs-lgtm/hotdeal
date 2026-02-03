import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import time
import re
import sys
import io

# 터미널 출력 인코딩 설정 (Windows cmd 호환성)
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

# Supabase 설정
URL: str = "https://zvlntvovzffizoruwxqx.supabase.co"
KEY: str = "sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV"

class BaseCrawler:
    def __init__(self, supabase_url, supabase_key):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }

    def fetch_page(self, url, encoding='utf-8', retries=3):
        for i in range(retries):
            try:
                # FMKorea 등 일부 사이트는 헤더에 민감함
                headers = self.headers.copy()
                if 'fmkorea' in url:
                    headers.update({
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                        'Referer': 'https://www.fmkorea.com/'
                    })

                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    # [중요] 인코딩 에러 방지를 위한 안전한 디코딩
                    try:
                        return response.content.decode(encoding, errors='replace')
                    except LookupError:
                        # encoding 이름이 잘못된 경우 utf-8 fallback
                        return response.content.decode('utf-8', errors='replace')
                        
                print(f"[{i+1}/{retries}] 페이지 로딩 실패: {response.status_code} ({url})")
            except Exception as e:
                print(f"[{i+1}/{retries}] 네트워크 에러: {e}")
            
            if i < retries - 1:
                time.sleep((i + 1) * 2)
        return None
    
    def normalize_category(self, raw_cat):
        """
        카테고리를 표준화된 6개 분류로 매핑
        표준 카테고리: [컴퓨터, 디지털, 식품/건강, 가전/가구, 의류/잡화, 기타]
        """
        if not raw_cat:
            return "기타"
        
        cat = raw_cat.strip()
        
        # 1. 컴퓨터
        if cat in ["PC제품", "컴퓨터", "노트북", "PC부품", "모니터"]:
            return "컴퓨터"
            
        # 2. 디지털 (모바일, 카메라, 음향기기 등)
        if cat in ["디지털", "모바일", "상품권", "모바일/상품권", "SW/게임"]:
            return "디지털"
            
        # 3. 식품/건강
        if cat in ["식품/건강", "먹거리", "식품", "건강", "생활/식품"]:
            return "식품/건강"
            
        # 4. 가전/가구
        if cat in ["가전/가구", "가전제품", "가전", "가구", "인테리어"]:
            return "가전/가구"
            
        # 5. 의류/잡화
        if cat in ["의류/잡화", "의류", "패션", "뷰티", "잡화"]:
            return "의류/잡화"

        # Ppomppu 특화된 매핑 (부분 일치)
        if "컴퓨터" in cat: return "컴퓨터"
        if "디지털" in cat: return "디지털"
        if "식품" in cat or "건강" in cat: return "식품/건강"
        if "가전" in cat or "가구" in cat: return "가전/가구"
        if "의류" in cat or "잡화" in cat: return "의류/잡화"

        return "기타"

    def save_deal(self, data):
        try:
            # 카테고리 표준화 적용
            data['category'] = self.normalize_category(data.get('category'))
                
            self.supabase.table("hotdeals").upsert(data).execute()
            # 안전한 출력을 위해 encode/decode 처리
            safe_title = data['title'][:15].encode('utf-8', 'replace').decode('utf-8')
            print(f"[{data['source']}] {data['category']} | {safe_title}... | {data['price']}")
            return True
        except Exception as e:
            if '23505' in str(e) or 'duplicate key' in str(e):
                try:
                    self.supabase.table("hotdeals").update(data).eq("url", data['url']).execute()
                    safe_title = data['title'][:15].encode('utf-8', 'replace').decode('utf-8')
                    print(f"[{data['source']}] {data['category']} (UP) | {safe_title}... | {data['price']}")
                    return True
                except Exception as update_error:
                    print(f"업데이트 실패: {update_error}")
            else:
                print(f"저장 실패: {e}")
        return False

    def crawl(self):
        raise NotImplementedError("Subclasses must implement crawl method")


class PpomppuCrawler(BaseCrawler):
    def extract_price(self, title):
        try:
            match = re.search(r'[\(\[]\s*([\d,]+(?:원|만원|원)?)\s*(?:/|\]|\))', title)
            if match: return match.group(1).strip()
            match_won = re.search(r'([\d,]+(?:원|만원))', title)
            if match_won: return match_won.group(1).strip()
        except:
            pass
        return "가격미상"

    def crawl(self):
        print("\n=== [Ppomppu] 크롤링 시작 ===")
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
                if href.startswith('/'):
                    link = "https://www.ppomppu.co.kr" + href
                else:
                    link = "https://www.ppomppu.co.kr/zboard/" + href

                img_url = ""
                thumb_link = item.select_one('.baseList-thumb')
                if thumb_link and thumb_link.has_attr('tooltip') and 'P_img:' in thumb_link['tooltip']:
                    img_url = thumb_link['tooltip'].split('P_img:')[-1]
                
                if not img_url:
                    img_el = item.select_one('.baseList-thumb img')
                    if img_el and 'src' in img_el.attrs:
                        img_url = img_el['src']

                if img_url:
                    if img_url.startswith('//'): img_url = "https:" + img_url
                    elif not img_url.startswith('http'): img_url = "https://www.ppomppu.co.kr" + img_url

                price = self.extract_price(full_title)
                
                # 카테고리 추출
                category = "기타"
                cat_el = item.select_one('.baseList-small') 
                if cat_el:
                    raw_cat = cat_el.get_text().strip()
                    category = raw_cat.replace('[', '').replace(']', '').strip()

                comment_el = item.select_one('.baseList-c')
                comment_count = int(comment_el.get_text().strip()) if comment_el else 0

                data = {
                    "title": full_title,
                    "url": link,
                    "img_url": img_url,
                    "source": "Ppomppu",
                    "category": category,
                    "price": price,
                    "comment_count": comment_count
                }
                
                if self.save_deal(data):
                    count += 1
                time.sleep(0.05)
            except Exception as e:
                print(f"Ppomppu 항목 처리 중 에러: {e}")
                
        print(f"=== [Ppomppu] 크롤링 완료 ({count}건) ===")


class FMKoreaCrawler(BaseCrawler):
    def crawl(self):
        print("\n=== [FMKorea] 크롤링 시작 ===")
        url = "https://www.fmkorea.com/hotdeal"
        html = self.fetch_page(url) 
        
        if not html: return

        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select('.fm_best_widget._bd_pc li.li')
        
        if not items:
            items = soup.select('.bd_lst_wrp .bd_lst tr:not(.notice)')
        
        count = 0
        for item in items:
            try:
                title_el = item.select_one('h3.title a.hotdeal_var8')
                if not title_el: continue

                target_span = title_el.select_one('.ellipsis-target')
                title = target_span.get_text().strip() if target_span else title_el.get_text().strip()
                
                href = title_el['href']
                if href.startswith('/'):
                    link = "https://www.fmkorea.com" + href
                else:
                    link = href

                img_url = ""
                thumb_el = item.select_one('img.thumb')
                if thumb_el:
                    if thumb_el.get('data-original'):
                        img_url = thumb_el['data-original']
                    elif thumb_el.get('src'):
                        img_url = thumb_el['src']
                
                if img_url and img_url.startswith('//'):
                    img_url = "https:" + img_url

                info_div = item.select_one('.hotdeal_info')
                price = "가격미상"
                if info_div:
                    info_text = info_div.get_text()
                    price_match = re.search(r'가격:\s*([0-9,]+원)', info_text)
                    if price_match:
                        price = price_match.group(1)
                    else:
                        strongs = info_div.select('a.strong')
                        if len(strongs) >= 2:
                            price = strongs[1].get_text().strip()

                category = "기타"
                cat_el = item.select_one('.category a')
                if cat_el:
                    category = cat_el.get_text().strip()

                comment_count = 0
                comment_span = title_el.select_one('.comment_count')
                if comment_span:
                    c_text = comment_span.get_text().strip('[] ')
                    if c_text.isdigit():
                        comment_count = int(c_text)

                data = {
                    "title": title,
                    "url": link,
                    "img_url": img_url,
                    "source": "FMKorea",
                    "category": category,
                    "price": price,
                    "comment_count": comment_count
                 }
                
                if self.save_deal(data):
                    count += 1
                time.sleep(0.05)

            except Exception as e:
                print(f"FMKorea 항목 에러: {e}")
                
        print(f"=== [FMKorea] 크롤링 완료 ({count}건) ===")

def main():
    ppomppu = PpomppuCrawler(URL, KEY)
    fmkorea = FMKoreaCrawler(URL, KEY)

    ppomppu.crawl()
    fmkorea.crawl()

if __name__ == "__main__":
    main()