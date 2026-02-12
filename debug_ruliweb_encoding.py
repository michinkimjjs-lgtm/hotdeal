import requests

def debug_encoding():
    url = "https://bbs.ruliweb.com/market/board/1020?view=gallery"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    
    print(f"Fetching {url}...")
    res = requests.get(url, headers=headers)
    print(f"Status: {res.status_code}")
    print(f"Encoding (from headers): {res.encoding}")
    print(f"Apparent Encoding: {res.apparent_encoding}")
    
    print("\nText Preview (res.text):")
    print(res.text[:500])
    
    print("\nContent Decode UTF-8 (res.content.decode('utf-8')): ")
    try:
        print(res.content.decode('utf-8')[:500])
    except Exception as e:
        print(f"UTF-8 Decode Error: {e}")

if __name__ == "__main__":
    debug_encoding()
