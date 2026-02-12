import quopri
import re

def extract_html():
    input_file = 'fmkorea_sample.html.mhtml'
    output_file = 'fmkorea_sample.html'
    
    print(f"Reading {input_file}...")
    with open(input_file, 'rb') as f:
        content = f.read()
        
    # Find boundary
    # Look for boundary="..." in the header
    header_end = content.find(b'\r\n\r\n')
    if header_end == -1:
        # Fallback to just scanning for boundaries
        pass
        
    # The first part is usually the HTML.
    # Pattern: Boundary -> Content-Type: text/html -> Empty Line -> Content -> Boundary
    
    # Let's simple split by boundary
    # We can try to guess the boundary or just look for "Content-Type: text/html"
    
    start_marker = b'Content-Type: text/html'
    start_pos = content.find(start_marker)
    
    if start_pos == -1:
        print("Could not find text/html content.")
        return

    # Move to end of headers for this part
    # We look for \r\n\r\n after start_pos
    header_end_pos = content.find(b'\r\n\r\n', start_pos)
    if header_end_pos == -1:
        print("Could not find end of part headers.")
        return
        
    content_start = header_end_pos + 4
    
    # Validate encoding
    encoding_line_start = content.rfind(b'Content-Transfer-Encoding:', start_pos, header_end_pos)
    is_qp = False
    if encoding_line_start != -1:
        line_end = content.find(b'\r\n', encoding_line_start)
        line = content[encoding_line_start:line_end]
        if b'quoted-printable' in line:
            is_qp = True
            
    # Find next boundary
    # We need to recognize the boundary from the file header
    # Or just look for "------MultipartBoundary"
    
    # Let's take a chunk and find the next boundary line
    # A boundary line starts with -- and usually has many dashes
    
    # Simple hack: Read until next "------MultipartBoundary"
    next_boundary_pos = content.find(b'------MultipartBoundary', content_start)
    
    if next_boundary_pos == -1:
        # Maybe end of file?
        raw_html = content[content_start:]
    else:
        raw_html = content[content_start:next_boundary_pos]
        
    print(f"Extracted {len(raw_html)} bytes of raw content.")
    
    if is_qp:
        print("Decoding quoted-printable...")
        decoded_html = quopri.decodestring(raw_html)
    else:
        decoded_html = raw_html
        
    # Decode charset? usually utf-8
    try:
        final_html = decoded_html.decode('utf-8')
    except:
        try:
            final_html = decoded_html.decode('euc-kr')
        except:
            final_html = decoded_html.decode('latin1')
            
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_html)
        
    print(f"Saved to {output_file} ({len(final_html)} chars)")

if __name__ == "__main__":
    extract_html()
