import requests
from bs4 import BeautifulSoup

url = "https://bbs.ruliweb.com/market/board/1020?view=gallery"
headers = {'User-Agent': 'Mozilla/5.0'}
try:
    res = requests.get(url, headers=headers)
    print(f"Status Code: {res.status_code}")
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Save for inspection
    with open('ruliweb_gallery_debug.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("Saved ruliweb_gallery_debug.html")

    # Check for gallery specific tags
    # Usually gallery has a wrapper with cards
    cards = soup.select('ul.board_list_gallery > li')
    if cards:
        print(f"Found {len(cards)} gallery cards.")
        first_card = cards[0]
        img = first_card.find('img')
        print(f"First card img: {img}")
    else:
        print("No ul.board_list_gallery found.")
        # Try finding *any* img inside board_main
        board_main = soup.find('div', id='board_main') # It was id="board_main" class="board_main..." in header? No, div.board_main
        if not board_main:
             board_main = soup.find('div', class_='board_main')
             
        if board_main:
            imgs = board_main.select('img')
            print(f"Found {len(imgs)} imgs in board_main.")

except Exception as e:
    print(f"Error: {e}")
