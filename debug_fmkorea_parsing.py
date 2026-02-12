from bs4 import BeautifulSoup
import urllib.parse
import re

def test_parsing():
    print("Loading fmkorea_sample.html...")
    with open('fmkorea_sample.html', 'r', encoding='utf-8') as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # Logic to be added to crawler.py
    buy_link = None
    
    # 1. Look for .hotdeal_url
    link_el = soup.select_one('a.hotdeal_url')
    if link_el:
        print(f"Found .hotdeal_url: {link_el}")
        href = link_el.get('href')
        print(f"Raw href: {href}")
        
        if 'link.fmkorea.org' in href and 'url=' in href:
            parsed = urllib.parse.urlparse(href)
            qs = urllib.parse.parse_qs(parsed.query)
            if 'url' in qs:
                buy_link = qs['url'][0]
                print(f"Extracted URL param: {buy_link}")
        else:
            buy_link = href
            
    if not buy_link:
        print("Failed to find buy link in .hotdeal_url")
        
    print(f"Final Buy Link: {buy_link}")

if __name__ == "__main__":
    test_parsing()
