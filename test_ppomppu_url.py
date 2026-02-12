import requests

def test_url():
    # User provided filename
    filename = "20260208211544_LAdNvOvNaH.jpeg"
    
    # Logic: YYYYMMDD... -> data3/YYYY/MMDD/filename
    year = filename[:4]
    month_day = filename[4:8]
    
    base_urls = [
        "https://cdn.ppomppu.co.kr/zboard/data3",
        "https://cdn2.ppomppu.co.kr/zboard/data3",
        "https://www.ppomppu.co.kr/zboard/data3"
    ]
    
    paths = [
        f"{year}/{month_day}/{filename}",
        f"{year}/{month_day}/900w_{filename}" # Sometimes 900w_ is prepended?
    ]
    
    print(f"Testing reconstruction for: {filename}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.ppomppu.co.kr/'
    }

    for base in base_urls:
        for path in paths:
            url = f"{base}/{path}"
            try:
                print(f"Checking: {url}")
                res = requests.head(url, headers=headers, timeout=2)
                print(f"  Status: {res.status_code}")
                if res.status_code == 200:
                    print(f"  ✅ FOUND! Correct URL pattern identified.")
                    return
            except Exception as e:
                print(f"  Error: {e}")

if __name__ == "__main__":
    test_url()
