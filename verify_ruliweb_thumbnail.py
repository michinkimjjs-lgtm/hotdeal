import requests
from bs4 import BeautifulSoup

url = "https://bbs.ruliweb.com/market/board/1020?view=thumbnail"
headers = {'User-Agent': 'Mozilla/5.0'}
try:
    res = requests.get(url, headers=headers)
    print(f"Status Code: {res.status_code}")
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Check for img tags in main content
    # In list view it was table.board_list_table -> tr.table_body
    # In thumbnail view, structure might be different, commonly ul > li or div.card
    
    # 1. Try to find the container
    # Based on previous HTML, container might be 'board_main'
    board_main = soup.find('div', class_='board_main')
    if board_main:
        imgs = board_main.find_all('img')
        print(f"Found {len(imgs)} images in board_main.")
        for i, img in enumerate(imgs[:5]):
            print(f"Image {i}: {img}")
            
        # Check for specific deal item structure in thumbnail view
        # Usually it's something like li.item or tr with thumb class
        items = soup.select('ul.board_list_gallery > li')
        if items:
            print(f"Found {len(items)} gallery items via ul.board_list_gallery.")
        else:
             print("No ul.board_list_gallery found. Checking table structure:")
             trs = soup.select('table.board_list_table tr')
             print(f"Found {len(trs)} table rows.")
             thumb_tds = soup.select('td.thumb')
             print(f"Found {len(thumb_tds)} thumb tds.")
             if thumb_tds:
                 print(f"Sample thumb td: {thumb_tds[0]}")

except Exception as e:
    print(f"Error: {e}")
