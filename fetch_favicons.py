import requests
from io import BytesIO
from PIL import Image
import os

def download_and_save_favicon(url, name):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        img = Image.open(BytesIO(response.content))
        
        # Convert to RGBA if not already (to handle transparency)
        img = img.convert("RGBA")
        
        # Resize to standard size for consistency (e.g., 64x64 or 32x32) - let's go with 64x64 for quality
        img = img.resize((64, 64), Image.LANCZOS)
        
        save_path = f"e:/an/Hot/assets/{name}_icon.png"
        img.save(save_path, "PNG")
        print(f"Saved {name} icon to {save_path}")
        return True
    except Exception as e:
        print(f"Failed to save {name} icon from {url}: {e}")
        return False

# Official Favicon URLs (identified from common patterns)
# Ppomppu: https://www.ppomppu.co.kr/favicon.ico
# FMKorea: https://www.fmkorea.com/favicon.ico (or check html)
# Ruliweb: https://bbs.ruliweb.com/favicon.ico (need to verify)

icons = [
    ("https://www.ppomppu.co.kr/favicon.ico", "ppomppu"),
    ("https://www.fmkorea.com/favicon.ico", "fmkorea"), 
    # Ruliweb typically uses a specific subpath, checking common ones
    # Trying the main site first.
    ("https://ruliweb.com/favicon.ico", "ruliweb") 
]

# Note: Ruliweb might need a specific one.
# Let's inspect Ruliweb HTML if the generic one fails or looks wrong.
# But for now, try generic.

for url, name in icons:
    download_and_save_favicon(url, name)
