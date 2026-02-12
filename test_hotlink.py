import requests

def test_hotlink():
    test_url_cdn = "https://cdn.ppomppu.co.kr/zboard/data3/2026/0209/900w_20260209095531_DM0lM0ngM5.jpeg"
    test_url_cdn2 = "https://cdn2.ppomppu.co.kr/zboard/data3/2026/0209/900w_20260209095531_DM0lM0ngM5.jpeg"
    
    headers_no_referer = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        # No Referer
    }
    
    headers_referer = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://www.ppomppu.co.kr/'
    }
    
    print("Testing CDN (No Referer)...")
    try:
        r = requests.head(test_url_cdn, headers=headers_no_referer, timeout=3)
        print(f"CDN Status: {r.status_code}")
    except Exception as e:
        print(f"CDN Error: {e}")

    print("\nTesting CDN2 (No Referer)...")
    try:
        r = requests.head(test_url_cdn2, headers=headers_no_referer, timeout=3)
        print(f"CDN2 Status: {r.status_code}")
    except Exception as e:
        print(f"CDN2 Error: {e}")

    print("\nTesting CDN (Vercel Referer)...")
    headers_vercel = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://hotdeal-olive.vercel.app/'
    }
    try:
        r = requests.head(test_url_cdn, headers=headers_vercel, timeout=3)
        print(f"CDN (Vercel) Status: {r.status_code}")
        print(f"CDN (Vercel) Content-Type: {r.headers.get('Content-Type')}")
    except Exception as e:
        print(f"CDN (Vercel) Error: {e}")

    print("\nTesting CDN2 (Vercel Referer)...")
    try:
        r = requests.head(test_url_cdn2, headers=headers_vercel, timeout=3)
        print(f"CDN2 (Vercel) Status: {r.status_code}")
        if r.status_code == 302:
            print(f"CDN2 (Vercel) Redirect: {r.headers.get('Location')}")
    except Exception as e:
        print(f"CDN2 (Vercel) Error: {e}")

if __name__ == "__main__":
    test_hotlink()
