import logging
import time
import sys
import io
from crawler import PpomppuCrawler, FMKoreaCrawler, URL, KEY

# crawler.py에서 설정한 로거를 가져옴
logger = logging.getLogger("crawler")

def main():
    # 10분마다 실행
    INTERVAL_MINUTES = 10 
    INTERVAL_SECONDS = INTERVAL_MINUTES * 60

    logging.info(f"🚀 [Auto Runner] 자동 크롤링을 시작합니다. ({INTERVAL_MINUTES}분 간격)")
    print("종료하려면 Ctrl+C를 누르세요.\n")

    ppomppu = PpomppuCrawler(URL, KEY)
    fmkorea = FMKoreaCrawler(URL, KEY)

    while True:
        try:
            # 크롤링 실행
            logging.info("크롤링 루프 시작")
            ppomppu.crawl()
            fmkorea.crawl()
            # Ruliweb 추가
            from crawler import RuliwebCrawler
            ruliweb = RuliwebCrawler(URL, KEY) # Note: Creating instance here for safety if not initialized outside
            ruliweb.crawl()
            
            # 다음 실행까지 대기
            logging.info(f"✅ 일시 완료. {INTERVAL_MINUTES}분 대기 중... ({time.strftime('%H:%M:%S')} 재개 예정)")
            time.sleep(INTERVAL_SECONDS)
            
        except KeyboardInterrupt:
            logging.info("🛑 사용자에 의해 중단되었습니다.")
            break
        except Exception as e:
            logging.error(f"❌ 예상치 못한 에러 발생: {e}", exc_info=True)
            logging.info("1분 후 재시도합니다.")
            time.sleep(60)

if __name__ == "__main__":
    main()
