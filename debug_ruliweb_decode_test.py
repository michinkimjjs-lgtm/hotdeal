import requests
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def debug_decode():
    url = "https://bbs.ruliweb.com/market/board/1020?view=gallery"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    
    print(f"Fetching {url}...")
    res = requests.get(url, headers=headers)
    print(f"Status: {res.status_code}")
    print(f"Headers Encoding: {res.encoding}")
    
    content = res.content
    print(f"Content Length: {len(content)}")
    
    # Try various decodings
    encodings = ['utf-8', 'euc-kr', 'cp949', 'latin-1']
    
    for enc in encodings:
        print(f"\n--- Decoding with {enc} ---")
        try:
            decoded = content.decode(enc)
            # Check for specific Korean keyword (e.g. '핫딜')
            if '핫딜' in decoded:
                 print("  >> SUCCESS! keyword '핫딜' found.")
            else:
                 print("  >> Decoded, but keyword '핫딜' not found (might be mojibake?).")
            preview = decoded[:100].replace('\n', ' ')
            print(f"  Preview: {preview}")
        except Exception as e:
            print(f"  >> FAILED: {e}")

if __name__ == "__main__":
    debug_decode()
