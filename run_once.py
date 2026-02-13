import logging
import sys
import os
import time
from crawler import PpomppuCrawler, FMKoreaCrawler, RuliwebCrawler

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("crawler")

def main():
    logger.info("🚀 [Cloud Runner] GitHub Actions 크롤링 시작")

    # Load Secrets from Environment Variables (GitHub Secrets)
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

    if not SUPABASE_URL:
        logger.error("❌ [오류] SUPABASE_URL이 없습니다. Settings > Secrets에 등록되었는지 확인해주세요.")
    if not SUPABASE_KEY:
        logger.error("❌ [오류] SUPABASE_KEY가 없습니다. Settings > Secrets에 등록되었는지 확인해주세요.")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        sys.exit(1)

    try:
        # Initialize Crawlers
        logger.info("🛠️ 크롤러 초기화 중...")
        ppomppu = PpomppuCrawler(SUPABASE_URL, SUPABASE_KEY)
        fmkorea = FMKoreaCrawler(SUPABASE_URL, SUPABASE_KEY)
        ruliweb = RuliwebCrawler(SUPABASE_URL, SUPABASE_KEY)

        # Run Crawlers
        logger.info("--- 뽐뿌 크롤링 시작 ---")
        ppomppu.crawl(limit=10) # 1회 실행 시 최신 10개만 확인 (효율성)
        
        logger.info("--- 펨코 크롤링 시작 ---")
        fmkorea.crawl(limit=10)

        logger.info("--- 루리웹 크롤링 시작 ---")
        ruliweb.crawl(limit=10)
        
        logger.info("✅ 모든 크롤링 작업이 완료되었습니다.")

    except Exception as e:
        logger.error(f"❌ 크롤링 중 치명적인 오류 발생: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
