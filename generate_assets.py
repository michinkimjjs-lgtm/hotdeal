from PIL import Image, ImageDraw, ImageFont
import os
import requests
from io import BytesIO

ASSETS_DIR = "assets"
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

# URL for high-quality Fire Emoji (Google Noto Emoji)
EMOJI_URL = "https://raw.githubusercontent.com/googlefonts/noto-emoji/main/png/512/emoji_u1f525.png"

def download_emoji():
    print(f"Downloading emoji from {EMOJI_URL}...")
    try:
        response = requests.get(EMOJI_URL)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert("RGBA")
    except Exception as e:
        print(f"Failed to download emoji: {e}")
        return None

def create_favicon(emoji_img):
    if not emoji_img: return
    # Resize to standard favicon sizes (e.g. 192x192)
    img = emoji_img.resize((192, 192), Image.Resampling.LANCZOS)
    img.save(f"{ASSETS_DIR}/favicon.png")
    print("Created favicon.png from emoji")

def create_og_image(emoji_img):
    width, height = 1200, 630
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    
    # Load Font
    try:
        font_path = "C:/Windows/Fonts/malgunbd.ttf" # Bold
        font_large = ImageFont.truetype(font_path, 100)
        font_medium = ImageFont.truetype(font_path, 50)
    except:
        print("Font not found, using default.")
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()

    # Text
    title = "핫딜모음"
    subtitle = "hotdeal.zip"
    
    # Measure text
    try:
        bbox_title = draw.textbbox((0, 0), title, font=font_large)
        w_title = bbox_title[2] - bbox_title[0]
        h_title = bbox_title[3] - bbox_title[1]
        
        bbox_sub = draw.textbbox((0, 0), subtitle, font=font_medium)
        w_sub = bbox_sub[2] - bbox_sub[0]
        h_sub = bbox_sub[3] - bbox_sub[1]
    except AttributeError:
        w_title, h_title = draw.textsize(title, font=font_large)
        w_sub, h_sub = draw.textsize(subtitle, font=font_medium)
        
    # Icon config
    icon_size = 150
    gap = 40
    
    # Total width of content (Icon + Gap + Text)
    # Text block width is max(w_title, w_sub)
    text_block_w = max(w_title, w_sub)
    total_w = icon_size + gap + text_block_w
    
    start_x = (width - total_w) // 2
    center_y = height // 2
    
    # Paste Emoji Icon
    if emoji_img:
        icon_resized = emoji_img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        # Paste with mask
        icon_y = center_y - icon_size // 2 - 20 # slightly up
        img.paste(icon_resized, (int(start_x), int(icon_y)), icon_resized)
    
    # Draw Text
    text_x = start_x + icon_size + gap
    text_y_title = center_y - h_title // 2 - 30
    draw.text((text_x, text_y_title), title, font=font_large, fill="black")
    
    text_y_sub = text_y_title + h_title + 15
    # Center subtitle relative to title or left align?
    # Let's align left with title
    draw.text((text_x, text_y_sub), subtitle, font=font_medium, fill="gray")
    
    img.save(f"{ASSETS_DIR}/og_image.png")
    print("Created og_image.png with emoji")

if __name__ == "__main__":
    emoji = download_emoji()
    if emoji:
        create_favicon(emoji)
        create_og_image(emoji)
    else:
        print("Could not generate assets due to download failure.")
