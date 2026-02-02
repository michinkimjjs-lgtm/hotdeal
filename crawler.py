import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import time
import re
import random

# 1. Supabase 설정 (본인의 정보로 변경 필요)
URL: str = "https://zvlntvovzffizoruwxqx.supabase.co"
KEY: str = "sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV"

class HotDealCrawler:
    def __init__(self, supabase_url, supabase_key):
        """
        초기화: Supabase 클라이언트를 생성합니다.
        """
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def fetch_page(self, url, retries=3):
        """
        네트워크 오류 시 재시도 로직이 포함된 페이지 요청 함수
        """
        for i in range(retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    return response.text
                print(f"[{i+1}/{retries}] 페이지 로딩 실패: {response.status_code}")
            except Exception as e:
                print(f"[{i+1}/{retries}] 네트워크 에러 발생: {e}")
            
            if i < retries - 1:
                wait_time = (i + 1) * 2 + random.uniform(0, 1)
                print(f"{wait_time:.1f}초 후 다시 시도합니다...")
                time.sleep(wait_time)
        return None

    def extract_price(self, title):
        """
        게시글 제목에서 가격 정보를 추출합니다.
        """
        # 1. 괄호 안의 가격 정보 (예: (69,000/무료) 등)
        match = re.search(r'[\(\[]\s*([\d,]+(?:원|만원|원)?)\s*(?:/|\]|\))', title)
        if match:
            return match.group(1).strip()
        
        # 2. '원' 또는 '만원' 키워드 앞의 숫자
        match_won = re.search(r'([\d,]+(?:원|만원))', title)
        if match_won:
            return match_won.group(1).strip()
            
        return "가격미상"

    def crawl_ppomppu(self):
        """
        뽐뿌 게시판을 크롤링하고 Supabase에 데이터를 저장합니다.
        """
        print("\n🚀 [Ppomppu] 크롤링을 시작합니다...")
        target_url = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
        html = self.fetch_page(target_url)
        
        if not html:
            print("❌ 데이터를 가져오는 데 실패하여 크롤링을 중단합니다.")
            return

        soup = BeautifulSoup(html, 'html.parser')
        # 게시글 목록 선택 (뽐뿌 특유의 클래스명)
        items = soup.select('tr.common-list0, tr.common-list1')
        
        success_count = 0
        error_count = 0

        for item in items:
            try:
                # 제목 요소 찾기
                title_el = item.select_one('font.list_title')
                if not title_el:
                    continue
                
                full_title = title_el.get_text().strip()
                # 뽐뿌 링크는 상대 경로인 경우가 많으므로 절대 경로로 변환
                link_el = item.select_one('td:nth-child(3) > a')
                if not link_el:
                    continue
                link = "https://www.ppomppu.co.kr/zboard/" + link_el['href']
                
                # 썸네일
                img_el = item.select_one('.thumb_border')
                img_url = "https:" + img_el['src'] if img_el else ""
                
                # 가격 추출
                price = self.extract_price(full_title)
                
                # 데이터 구성 (Supabase 테이블 컬럼과 일치)
                data = {
                    "title": full_title,
                    "url": link,
                    "img_url": img_url,
                    "source": "Ppomppu",
                    "category": "기타",
                    "price": price
                }
                
                # Supabase Upsert (url을 기준으로 중복 체크)
                res = self.supabase.table("hotdeals").upsert(data, on_conflict="url").execute()
                
                if hasattr(res, 'data') and len(res.data) > 0:
                    print(f"✅ 저장 성공: {full_title[:25]}... [{price}]")
                    success_count += 1
                else:
                    # upsert의 경우 데이터가 변하지 않으면 res.data가 비어있을 수 있음
                    print(f"ℹ️ 업데이트됨(또는 변화없음): {full_title[:25]}...")
                    success_count += 1
                    
            except Exception as e:
                print(f"❌ 개별 항목 처리 중 에러 발생: {e}")
                error_count += 1

        print(f"\n✨ 크롤링 완료! (성공: {success_count}, 에러: {error_count})")

if __name__ == "__main__":
    # 크롤러 실행
    crawler = HotDealCrawler(URL, KEY)
    crawler.crawl_ppomppu()
