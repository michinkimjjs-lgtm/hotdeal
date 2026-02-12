import requests
from bs4 import BeautifulSoup
import sys

# Encoding fix
sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0 Safari/537.36'
}

def fetch(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        return res.content
    except: return None

def debug_fmkorea():
    print("\n=== DEBUG FMKOREA ===")
    # Recent hotdeal list to get a valid live link
    list_url = "https://www.fmkorea.com/hotdeal"
    html = fetch(list_url)
    if not html: return
    soup = BeautifulSoup(html, 'html.parser')
    
    # Get first item
    item = soup.select_one('.fm_best_widget._bd_pc li.li h3.title a.hotdeal_var8')
    if not item:
        print("Failed to find item in list")
        return
        
    link = "https://www.fmkorea.com" + item['href']
    print(f"Target URL: {link}")
    
    d_html = fetch(link)
    d_soup = BeautifulSoup(d_html, 'html.parser')
    
    # Dump likely areas
    print("\n[Searching for Links]")
    # 1. Look for 'a' tags with http/https in href that are NOT fmkorea
    all_a = d_soup.select('a')
    for a in all_a:
        href = a.get('href', '')
        if href.startswith('http') and 'fmkorea.com' not in href and 'javascript' not in href:
            print(f"External Link: {href}")
            print(f"  Parent: <{a.parent.name} class='{a.parent.get('class')}'>")
            print(f"  Text: {a.get_text().strip()}")

def debug_ppomppu():
    print("\n=== DEBUG PPOMPPU ===")
    url = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
    html = fetch(url) # euc-kr might be needed but requests usually handles auto content
    if not html: return
    # Try decoding
    try:
        txt = html.decode('euc-kr', errors='replace')
    except:
        txt = html.decode('utf-8', errors='replace')
        
    soup = BeautifulSoup(txt, 'html.parser')
    item = soup.select_one('tr.baseList:not(.baseNotice) .baseList-title')
    if not item: 
        print("Failed to find item in list")
        return
        
    link = "https://www.ppomppu.co.kr/zboard/" + item['href']
    print(f"Target URL: {link}")
    
    d_html = fetch(link)
    try:
        d_txt = d_html.decode('euc-kr', errors='replace')
    except:
        d_txt = d_html.decode('utf-8', errors='replace')
        
    d_soup = BeautifulSoup(d_txt, 'html.parser')
    
    print("\n[Searching for Links]")
    # Check .wordfix or .han
    wordfix = d_soup.select('.wordfix a')
    for a in wordfix:
        print(f".wordfix link: {a.get('href')}")
        
    han = d_soup.select('.han a')
    for a in han:
        href = a.get('href', '')
        if 'ppomppu' not in href:
            print(f".han external link: {href}")

if __name__ == "__main__":
    debug_fmkorea()
    debug_ppomppu()
