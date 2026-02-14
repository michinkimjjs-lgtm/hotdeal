
import tls_client
import sys

def test_encoding():
    url = "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu"
    session = tls_client.Session(client_identifier="chrome_120")
    
    print("Fetching Ppomppu with tls_client...")
    try:
        response = session.get(url)
        content_bytes = response.content
        
        # Check for signature of bad decoding
        # If content_bytes contains UTF-8 replacement char bytes \xef\xbf\xbd, it means it was decoded/mangled
        if b'\xef\xbf\xbd' in content_bytes:
            print("FOUND UTF-8 replacement character bytes in .content!")
            print("   This confirms tls_client is pre-decoding EUC-KR as UTF-8.")
            
            # Demonstrate the mojibake
            try:
                decoded = content_bytes.decode('euc-kr')
                print(f"   Decoded as EUC-KR snippet: {decoded[:100].encode('cp949', 'ignore').decode('cp949')}")
                if "占쏙옙" in decoded:
                    print("   MOJIBAKE '占쏙옙' reproduced!")
            except:
                print("   Could not decode with EUC-KR")
        else:
            print("No replacement chars found. Attempting proper decode...")
            try:
                decoded = content_bytes.decode('euc-kr')
                print("   Success! Title sample:")
                # print title
            except Exception as e:
                print(f"   Decode failed: {e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_encoding()
