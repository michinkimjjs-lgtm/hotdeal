import requests

url = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Referer': 'https://www.ppomppu.co.kr/'
}

print(f"URL 요청 중: {url}")
try:
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'euc-kr' # 뽐뿌 인코딩 강제 설정
    
    print(f"상태 코드: {response.status_code}")
    print(f"데이터 길이: {len(response.text)}")
    
    # HTML 파일로 저장
    with open("debug_ppomppu.html", "w", encoding="utf-8") as f:
        f.write(response.text)
        
    print("debug_ppomppu.html 파일로 저장 완료.")
    
    # 내용 확인 (common-list 포함 여부)
    if "common-list" in response.text:
       print("✅ HTML 내에 'common-list' 클래스가 발견되었습니다.")
    else:
       print("⚠️ HTML 내에 'common-list' 클래스가 없습니다. (차단되었거나 구조 변경)")
       # 주요 키워드로 차단 여부 추측
       if "captcha" in response.text.lower():
           print("캡차(Captcha)가 감지되었습니다.")
       if "access denied" in response.text.lower():
           print("접근 거부(Access Denied)가 감지되었습니다.")

except Exception as e:
    print(f"에러 발생: {e}")
