import requests
from bs4 import BeautifulSoup
import re
import sys
import io
import time
import random

# 인코딩 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Global Session
session = requests.Session()

def fetch_page(url, referer=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': referer if referer else 'https://www.google.com/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    try:
        res = session.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            return res.text
        else:
            print(f"Fetch failed: {res.status_code} ({url})")
            return None
    except Exception as e:
        print(f"Fetch error: {e}")
        return None

def debug_fmkorea():
    print("=== FMKorea Single Item Debug (Local File) ===")
    filename = "fmkorea_sample.html"
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            d_html = f.read()
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return

    print(f"Loaded {len(d_html)} bytes from {filename}")
    
    d_soup = BeautifulSoup(d_html, 'html.parser')
    
    # 0. Title (Try to find it in title tag or h1)
    title = ""
    t_el = d_soup.select_one('.np_18px span.np_18px_span') # Common in detail
    if not t_el: t_el = d_soup.select_one('h1')
    if t_el: title = t_el.get_text().strip()
    print(f"Title: {title}")

    # 1. Price (Improved Regex)
    price = "가격미상"
    info_div = d_soup.select_one('.hotdeal_info')
    if info_div:
        print(f"\n[Hotdeal Info HTML]\n{info_div.prettify()}\n")
        p_txt = info_div.get_text()
        p_match = re.search(r'가격\s*:\s*(?:[^\d\s]*\s*)?([0-9,]+(?:원)?)', p_txt)
        if p_match: price = p_match.group(1)
        
        # Info Links
        a_tags = info_div.select('a')
        for a in a_tags:
             href = a.get('href', '')
             print(f"  -> Info Link: {href}")

    print(f"Price: {price}")
    
    # 2. Content Links
    target = d_soup.select_one('.rd_body') or d_soup.select_one('div.rd_body')
    content_html = ""
    if target:
        # Check for images
        imgs = target.select('img')
        for img in imgs:
            print(f"Content Image: {img.get('src') or img.get('data-original')}")

        # Dump partial content HTML to see structure
        # print(f"\n[Content HTML Preview]\n{target.prettify()[:1000]}...\n")

        # Link Scan - Print ALL links to find candidates
        links = target.select('a')
        for a in links:
            href = a.get('href', '')
            print(f"Content Link Found: {href} (Text: {a.get_text().strip()})")

        # Clean content
        for tag in target(['script', 'style', 'iframe']): tag.decompose()
        content_html = str(target)

    else:
        print("Content (.rd_body) not found.")

if __name__ == "__main__":
    debug_fmkorea()


if __name__ == "__main__":
    debug_fmkorea()
