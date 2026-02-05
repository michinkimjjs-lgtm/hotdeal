import requests
import os

# 타임아웃을 짧게 설정하여 멈춤 방지
TIMEOUT = 15

sites = {
    "ruliweb": "https://bbs.ruliweb.com/market/board/1020",
    "fmkorea": "https://www.fmkorea.com/hotdeal",
    "ppomppu": "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
}

headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

print("Starting robust diagnosis...")

for name, url in sites.items():
    print(f"Fetching {name}...")
    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        
        # 파일로 저장하여 분석 (UTF-8)
        filename = f"raw_sample_{name}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"Saved {filename} ({len(response.text)} bytes)")
        
    except Exception as e:
        print(f"Error fetching {name}: {e}")

print("Diagnosis download complete.")
