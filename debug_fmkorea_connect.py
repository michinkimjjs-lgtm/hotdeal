import requests

def test_connect():
    url = "https://www.fmkorea.com/hotdeal"
    
    strategies = [
        ("Base (Google Ref)", {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Referer': 'https://www.google.com/'
        }),
        ("FMKorea Ref", {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Referer': 'https://www.fmkorea.com/'
        }),
        ("No Sec-CH", {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
        }),
        ("Mobile UA", {
             'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36',
             'Referer': 'https://m.fmkorea.com/'
        })
    ]
    
    import time
    for name, headers in strategies:
        print(f"\nTesting Strategy: {name}")
        try:
            res = requests.get(url, headers=headers, timeout=10)
            print(f"Status Code: {res.status_code}")
            if res.status_code == 200:
                print(">>> SUCCESS! <<<")
                return
            else:
                 print(f"Failed. Preview: {res.text[:100]}")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(2)

if __name__ == "__main__":
    test_connect()
