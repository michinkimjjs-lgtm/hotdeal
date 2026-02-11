import logging
import time
import sys
import io
from crawler import PpomppuCrawler, FMKoreaCrawler, URL, KEY

import json
import os

# crawler.py에서 설정한 로거를 가져옴 (없으면 기본 설정)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("crawler")

CONFIG_FILE = "config.json"

def load_config():
    default_config = {"crawling_enabled": True, "interval_minutes": 10}
    if not os.path.exists(CONFIG_FILE):
        return default_config
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"설정 파일 읽기 실패 ({e}), 기본값을 사용합니다.")
        return default_config

def main():
    logger.info("🚀 [Auto Runner] 자동 크롤링 서비스 시작")
    print("종료하려면 Ctrl+C를 누르세요.\n")

    ppomppu = PpomppuCrawler(URL, KEY)
    fmkorea = FMKoreaCrawler(URL, KEY)
    from crawler import RuliwebCrawler # Lazy import if needed, or structured better
    ruliweb = RuliwebCrawler(URL, KEY)

    while True:
        try:
            config = load_config()
            interval_minutes = config.get("interval_minutes", 10)
            is_enabled = config.get("crawling_enabled", True)

            if not is_enabled:
                logger.info(f"⏸️ 크롤링이 일시 중지되었습니다. (config.json: crawling_enabled=false)")
                logger.info(f"   -> 1분 후 다시 확인합니다.")
                time.sleep(60)
                continue

            # 크롤링 실행
            logger.info("==== 크롤링 루프 시작 ====")
            ppomppu.crawl()
            fmkorea.crawl()
            ruliweb.crawl()
            
            # 다음 실행까지 대기
            next_run_time = time.time() + (interval_minutes * 60)
            next_run_str = time.strftime('%H:%M:%S', time.localtime(next_run_time))
            logger.info(f"✅ 루프 완료. {interval_minutes}분 대기 중... ({next_run_str} 재개 예정)")
            
            time.sleep(interval_minutes * 60)
            
        except KeyboardInterrupt:
            logger.info("🛑 사용자에 의해 중단되었습니다.")
            break
        except Exception as e:
            logger.error(f"❌ 예상치 못한 에러 발생: {e}", exc_info=True)
            logger.info("1분 후 재시도합니다.")
            time.sleep(60)

if __name__ == "__main__":
    main()
