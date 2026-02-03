import requests
import sys

# 콘솔 출력 인코딩 강제 설정 (윈도우 이슈 방지)
sys.stdout.reconfigure(encoding='utf-8')

url = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
}

try:
    with open("log.txt", "w", encoding="utf-8") as log:
        log.write("Start\n")
        response = requests.get(url, headers=headers, timeout=10)
        log.write(f"Status: {response.status_code}\n")
        
        # 인코딩 설정
        response.encoding = 'euc-kr' 
        
        # 파일로 내용 저장
        with open("debug_ppomppu.html", "w", encoding="utf-8") as f:
            f.write(response.text)
            
        log.write("Saved debug_ppomppu.html\n")
        
        if "common-list" in response.text:
            log.write("Found common-list\n")
        else:
            log.write("common-list NOT found\n")
            
except Exception as e:
    with open("log.txt", "a", encoding="utf-8") as log:
        log.write(f"Error: {e}\n")
