import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import time
import re
import random
import sys
import io

# 터미널 출력 인코딩을 UTF-8로 강제 설정하여 이모지 및 한글 깨짐 방지
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

# 1. Supabase 설정
URL: str = "https://zvlntvovzffizoruwxqx.supabase.co"
KEY: str = "sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV"

class HotDealCrawler:
    def __init__(self, supabase_url, supabase_key):
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def fetch_page(self, url, retries=3):
        for i in range(retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                # 뽐뿌는 EUC-KR을 사용하므로 명시적으로 설정
                response.encoding = 'euc-kr' 
                if response.status_code == 200:
                    return response.text
                print(f"[{i+1}/{retries}] 페이지 로딩 실패: {response.status_code}")
            except Exception as e:
                print(f"[{i+1}/{retries}] 네트워크 에러 발생: {e}")
            
            if i < retries - 1:
                time.sleep((i + 1) * 2)
        return None

    def extract_price(self, title):
        # 괄호 안의 가격 정보 추출
        match = re.search(r'[\(\[]\s*([\d,]+(?:원|만원|원)?)\s*(?:/|\]|\))', title)
        if match:
            return match.group(1).strip()
        # '원' 키워드 기반 추출
        match_won = re.search(r'([\d,]+(?:원|만원))', title)
        if match_won:
            return match_won.group(1).strip()
        return "가격미상"

    def crawl_ppomppu(self):
        print("\n[Ppomppu] 데이터 수집 및 Supabase 전송을 시작합니다...")
        target_url = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
        html = self.fetch_page(target_url)
        
        if not html:
            print("데이터를 가져오지 못했습니다.")
            return

        soup = BeautifulSoup(html, 'html.parser')
        
        # [수정] 게시글 목록 선택 (새로운 클래스명 적용)
        items = soup.select('tr.baseList')
        
        if not items:
            print("게시글 목록을 찾을 수 없습니다. (선택자 불일치)")
            return

        success_count = 0
        error_count = 0

        for item in items:
            try:
                # 공지사항(Notice) 건너뛰기
                if 'baseNotice' in item.get('class', []):
                    continue

                # 1. 제목 및 링크 추출
                # 예: <a class='baseList-title' ...><span>...</span></a>
                title_el = item.select_one('.baseList-title')
                if not title_el:
                    continue
                
                full_title = title_el.get_text().strip()
                
                # 링크 경로 처리 (중복 경로 방지)
                href = title_el['href']
                if href.startswith('/'):
                    link = "https://www.ppomppu.co.kr" + href
                else:
                    link = "https://www.ppomppu.co.kr/zboard/" + href
                
                # 2. 이미지 추출 (tooltip or img tag)
                img_url = ""
                # 툴팁에서 고화질 이미지 우선 추출
                thumb_link = item.select_one('.baseList-thumb')
                if thumb_link and thumb_link.has_attr('tooltip'):
                    tooltip = thumb_link['tooltip'] # 예: P_img://cdn...
                    if 'P_img:' in tooltip:
                        img_url = tooltip.split('P_img:')[-1]
                
                # 툴팁 없으면 일반 이미지 태그 fallback
                if not img_url:
                    img_el = item.select_one('.baseList-thumb img')
                    if img_el and 'src' in img_el.attrs:
                        img_url = img_el['src']

                # 프로토콜 보정 (// -> https://)
                if img_url and img_url.startswith('//'):
                    img_url = "https:" + img_url
                elif img_url and not img_url.startswith('http'):
                    img_url = "https://www.ppomppu.co.kr" + img_url

                # 3. 가격 추출 (제목 기반)
                price = self.extract_price(full_title)
                
                # 4. 댓글 수 추출 (옵션)
                comment_el = item.select_one('.baseList-c')
                comment_count = int(comment_el.get_text().strip()) if comment_el else 0
                
                # 5. 데이터 구성
                data = {
                    "title": full_title,
                    "url": link,
                    "img_url": img_url,
                    "source": "Ppomppu",
                    "category": "기타",
                    "price": price,
                    "comment_count": comment_count
                 }
                
                # 6. Supabase 저장 (Upsert 구현)
                # 라이브러리 버전에 따라 upsert 동작이 다를 수 있어, 중복 에러 발생 시 Update 시도
                try:
                    self.supabase.table("hotdeals").upsert(data).execute()
                    print(f"수집(신규/갱신): {full_title[:15]}... | {price}")
                    success_count += 1
                except Exception as e:
                    # 중복 키 에러(23505)인 경우 Update 시도
                    if '23505' in str(e) or 'duplicate key' in str(e):
                        try:
                            self.supabase.table("hotdeals").update(data).eq("url", link).execute()
                            print(f"수집(업데이트): {full_title[:15]}... | {price}")
                            success_count += 1
                        except Exception as update_error:
                            print(f"업데이트 실패: {update_error}")
                            error_count += 1
                    else:
                        print(f"저장 실패: {e}")
                        error_count += 1
                        
                # 서버 부하 방지를 위한 미세 지연
                time.sleep(0.05)
                    
            except Exception as e:
                print(f"항목 처리 중 에러: {e}")
                error_count += 1

        print(f"\n작업 완료! (성공: {success_count}, 에러: {error_count})")

if __name__ == "__main__":
    crawler = HotDealCrawler(URL, KEY)
    crawler.crawl_ppomppu()