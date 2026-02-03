import time
import sys
import io
from crawler import PpomppuCrawler, FMKoreaCrawler

try:
    from crawler import URL, KEY
except ImportError:
    URL = "https://zvlntvovzffizoruwxqx.supabase.co"
    KEY = "sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV"

# 터미널 출력 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

def main():
    # 10분마다 실행
    INTERVAL_MINUTES = 10 
    INTERVAL_SECONDS = INTERVAL_MINUTES * 60

    print(f"🚀 [Auto Runner] 자동 크롤링을 시작합니다. ({INTERVAL_MINUTES}분 간격)")
    print("종료하려면 Ctrl+C를 누르세요.\n")

    ppomppu = PpomppuCrawler(URL, KEY)
    fmkorea = FMKoreaCrawler(URL, KEY)

    while True:
        try:
            # 크롤링 실행
            ppomppu.crawl()
            fmkorea.crawl()
            
            # 다음 실행까지 대기
            print(f"\n⏳ {INTERVAL_MINUTES}분 대기 중... ({time.strftime('%H:%M:%S')} 재개 예정)")
            time.sleep(INTERVAL_SECONDS)
            
        except KeyboardInterrupt:
            print("\n🛑 사용자에 의해 중단되었습니다.")
            break
        except Exception as e:
            print(f"\n❌ 예상치 못한 에러 발생: {e}")
            print("1분 후 재시도합니다.")
            time.sleep(60)

if __name__ == "__main__":
    main()
