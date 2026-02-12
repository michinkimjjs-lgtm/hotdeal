import tls_client
import sys

# Windows console encoding fix
sys.stdout.reconfigure(encoding='utf-8')

def test_encoding():
    print("=== Testing Ppomppu (EUC-KR) with tls_client ===")
    
    session = tls_client.Session(client_identifier="chrome_120")
    
    url = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
    
    try:
        response = session.get(url)
        print(f"Status: {response.status_code}")
        
        # Check if .text comes out correctly
        print("--- response.text snippet ---")
        print(response.text[:200]) 
        
        if "뽐뿌" in response.text:
             print("\n✅ '뽐뿌' found in .text -> Auto-decoding worked!")
        else:
             print("\n⚠️ '뽐뿌' NOT found in .text -> Encoding issue likely.")
             
             # Try manual decode
             try:
                 decoded = response.content.decode('euc-kr', errors='replace')
                 if "뽐뿌" in decoded:
                     print("✅ Manual decode (euc-kr) worked!")
             except Exception as e:
                 print(f"Manual decode failed: {e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_encoding()
