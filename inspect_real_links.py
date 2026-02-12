import requests
from bs4 import BeautifulSoup
import sys

# Windows mojibake fix
sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}

def inspect(url, source):
    print(f"\n--- Inspecting {source} : {url} ---")
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        encoding = 'euc-kr' if source == 'Ppomppu' else 'utf-8'
        
        # Ppomppu sometimes fails with euc-kr if mixed, try replace
        content = res.content.decode(encoding, errors='replace')
        soup = BeautifulSoup(content, 'html.parser')
        
        print(f"Title: {soup.title.string if soup.title else 'No Title'}")
        
        # 1. Look for explicit link containers
        if source == 'FMKorea':
            # Check for specific link table or div
            # Common patterns: .movie_info, .link_url, tr containing "링크"
            links = soup.select('div.hotdeal_info')
            for l in links: print(f"Hotdeal Info: {l.get_text().strip()}")
            
            # Check anchors in the whole header area
            header_links = soup.select('.qe_content .xe_content a') # Sometimes here?
            
            # FMKorea hotdeal often has link in a specific structure
            # Let's verify commonly known selector: .hotdeal_var8 is title link, 
            # inside detail, is there a 'Link' row?
            
            # Let's dump ALL 'a' tags that look external
            all_a = soup.select('a')
            for a in all_a:
                h = a.get('href', '')
                if 'coupang' in h or 'gmarket' in h or '11st' in h:
                    print(f"Found Candidate: {h} inside <{a.parent.name} class='{a.parent.get('class')}'>")

        elif source == 'Ppomppu':
            # Ppomppu usually has links in top table
            # .wordfix a, .han a
            # Look for anchors with external domains
            all_a = soup.select('a')
            for a in all_a:
                h = a.get('href', '')
                if 'coupang' in h or 'gmarket' in h or '11st' in h:
                    print(f"Found Candidate: {h} inside <{a.parent.name} class='{a.parent.get('class')}'>")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Use real recent URLs that are likely hotdeals
    # Update these with FRESH ones from the site if possible, or use generic ones
    inspect("https://www.fmkorea.com/index.php?mid=hotdeal&document_srl=7973784136&listStyle=list", "FMKorea") # Random recent ID
    inspect("https://www.ppomppu.co.kr/zboard/view.php?id=ppomppu&no=563500", "Ppomppu") # Random recent ID
