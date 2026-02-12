import requests
import random

class MockCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ]
        self.current_ua = random.choice(self.user_agents)

    def fetch_page(self, url, encoding='utf-8', retries=3, referer=None):
        for i in range(retries):
            try:
                headers = {
                    'User-Agent': self.current_ua,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate', # Exact match with crawler.py
                    'Referer': referer if referer else 'https://www.google.com/',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"'
                }
                print(f"Requesting {url} with headers:\n{headers}")
                response = self.session.get(url, headers=headers, timeout=15)
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    return response.text
                if response.status_code == 430:
                    print("Blocked (430)")
            except Exception as e:
                print(f"Error: {e}")
        return None

def test():
    c = MockCrawler()
    url = "https://www.fmkorea.com/hotdeal"
    html = c.fetch_page(url)
    if html:
        print("Success!")
    else:
        print("Failed.")

if __name__ == "__main__":
    test()
