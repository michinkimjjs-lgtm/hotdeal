import requests

url = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print(f"Requesting {url}...")
try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Encoding: {response.encoding}")
    response.encoding = 'euc-kr'
    print(f"Content Length: {len(response.text)}")
    print("--- First 500 chars ---")
    # 필터링해서 출력 (인코딩 문제 방지)
    clean_text = "".join(c for c in response.text[:500] if ord(c) < 65536)
    print(clean_text)
    print("--- End ---")
    
    if "common-list0" in response.text:
        print("Found 'common-list0' in HTML!")
    else:
        print("'common-list0' NOT found in HTML.")

except Exception as e:
    print(f"Error: {e}")
