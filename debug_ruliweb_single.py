import requests
from bs4 import BeautifulSoup
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def debug_ruliweb():
    # Specific URL from user
    target_url = "https://bbs.ruliweb.com/market/board/1020/read/101625?view=gallery"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    
    print(f"Fetching detail: {target_url}")
    d_res = requests.get(target_url, headers=headers)
    d_soup = BeautifulSoup(d_res.text, 'html.parser')
    
    # 1. Source Link Check
    print("\n--- Source Link (.source_url) ---")
    src_el = d_soup.select_one('.source_url a')
    if src_el:
        print(f"Found: {src_el.get('href')}")
    else:
        print("Not Found.")
        
    # 2. Content Link Check (Extract Buy Link Logic Simulation)
    print("\n--- Content Links ---")
    content = d_soup.select_one('.view_content') or d_soup.select_one('.board_main_view')
    if content:
        links = content.select('a')
        for a in links:
            print(f"Link: {a.get('href')}")
    else:
        print("Content not found.")
        
    # 3. Title Check
    title_el = d_soup.select_one('.subject_text')
    if title_el:
        print(f"\nTitle: {title_el.get_text().strip()}")

if __name__ == "__main__":
    debug_ruliweb()
