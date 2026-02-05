import requests
from bs4 import BeautifulSoup
import re

url = "https://www.fmkorea.com/hotdeal"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Referer': 'https://www.fmkorea.com/'
}

res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.content, 'html.parser')

# Get first item link
item = soup.select_one('.fm_best_widget._bd_pc li.li')
if not item:
    item = soup.select_one('.bd_lst_wrp .bd_lst tr:not(.notice)')

link = item.select_one('h3.title a.hotdeal_var8')['href']
if link.startswith('/'): link = "https://www.fmkorea.com" + link

print(f"Detail Link: {link}")

# Fetch detail page
res_detail = requests.get(link, headers=headers)
soup_detail = BeautifulSoup(res_detail.content, 'html.parser')

# Look for main images in the content
content = soup_detail.select_one('article')
if content:
    imgs = content.select('img')
    print(f"Found {len(imgs)} images in article")
    for i, img in enumerate(imgs[:3]):
        src = img.get('src') or img.get('data-original')
        print(f"Image {i+1}: {src}")

# Check thumbnail again
thumb_el = item.select_one('img.thumb')
print(f"List Thumbnail: {thumb_el.get('data-original') or thumb_el.get('src')}")
