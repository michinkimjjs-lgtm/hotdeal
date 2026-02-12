from crawler import FMKoreaCrawler
import sys

URL = "https://zvlntvovzffizoruwxqx.supabase.co"
KEY = "sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV"

crawler = FMKoreaCrawler(URL, KEY)
url = "https://www.fmkorea.com/9473932423"

print(f"Fetching {url} with Crawler Headers...")
html = crawler.fetch_page(url, referer="https://www.fmkorea.com/hotdeal")

if html:
    with open('fmkorea_debug_content.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Saved to fmkorea_debug_content.html")
else:
    print("Fetch returned None (Blocked?)")
