import requests
import sys

# Mojibake fix
sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}

def analyze(url, source):
    print(f"--- ANALYZING {source} : {url} ---")
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        encoding = 'euc-kr' if source == 'Ppomppu' else 'utf-8'
        html = res.content.decode(encoding, errors='replace')
        
        # Search for keywords and print context
        keywords = ['쇼핑몰', '가격', '배송', '링크', 'http']
        
        print(f"Total Length: {len(html)}")
        
        lines = html.split('\n')
        for i, line in enumerate(lines):
            for k in keywords:
                if k in line and len(line) < 500: # Context line
                    print(f"Line {i+1} : {line.strip()}")
                    # Print adjacent lines for context
                    if i+1 < len(lines): print(f"  + {lines[i+1].strip()}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Real recent URLs
    fmkorea_url = "https://www.fmkorea.com/7974345242" 
    ppomppu_url = "https://www.ppomppu.co.kr/zboard/view.php?id=ppomppu&no=563531" 
    
    analyze(fmkorea_url, "FMKorea")
    analyze(ppomppu_url, "Ppomppu")
