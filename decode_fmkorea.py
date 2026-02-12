import re
import base64
import os

def decode_char(c):
    return chr((ord(c) - 3 + 256) % 256)

def decode_fmkorea():
    print("Decoding debug_fmkorea.html...")
    with open('e:/an/Hot/debug_fmkorea.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the array
    match = re.search(r'var HpW = \[(.*?)\];', content, re.DOTALL)
    if not match:
        print("Array not found.")
        return

    array_str = match.group(1)
    # Parse array (handle quotes and newlines)
    items = [x.strip().strip('"') for x in array_str.split(',')]
    
    decoded_html = ""
    for item in items:
        if not item: continue
        # Slice 3, -3
        sliced = item[3:-3]
        try:
            # atob equivalent
            decoded_bytes = base64.b64decode(sliced)
            decoded_str = decoded_bytes.decode('latin1') # 'atob' returns binary string, usually latin1 in JS context
            
            chunk = ""
            for char in decoded_str:
                chunk += decode_char(char)
            decoded_html += chunk
        except Exception as e:
            print(f"Error decoding item {item}: {e}")
            
    # URL Decode (decodeURIComponent)
    from urllib.parse import unquote
    try:
        final_html = unquote(decoded_html)
    except:
        final_html = decoded_html

    print(f"Decoded Length: {len(final_html)}")
    try:
        print(f"Preview: {final_html[:200]}")
    except:
        print("Preview failed due to encoding.")
    
    with open('e:/an/Hot/decoded_fmkorea.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    print("Saved to decoded_fmkorea.html")

if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    decode_fmkorea()
