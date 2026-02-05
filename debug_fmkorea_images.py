
import os
import requests
from supabase import create_client

def check_supabase():
    url = 'https://dovqfujunoymsbnnlbth.supabase.co'
    key = os.getenv('SUPABASE_KEY')
    if not key:
        print("SUPABASE_KEY not found")
        return
    
    supabase = create_client(url, key)
    res = supabase.table('hot_deals').select('title, source, img_url').eq('source', 'FMKorea').order('created_at', desc=True).limit(5).execute()
    print("=== Current FMKorea Images in Supabase ===")
    for d in res.data:
        print(f"[{d['source']}] {d['title']}")
        print(f"URL: {d['img_url']}\n")

def test_thumbnail_sizes():
    # Using a known valid image ID
    img_id = "9455290107"
    date = "20260204"
    sizes = [
        "70x50",   # original desktop
        "140x100",  # mobile (current fix)
        "200x150", 
        "280x200", 
        "300x200",
        "400x300",
        "320x240"
    ]
    
    print("=== Testing Thumbnail Sizes ===")
    headers = {'User-Agent': 'Mozilla/5.0'}
    for s in sizes:
        url = f"https://image.fmkorea.com/filesn/cache/thumb/{date}/{img_id}_{s}.crop.webp"
        r = requests.get(url, headers=headers)
        print(f"{s}: {r.status_code}")

if __name__ == "__main__":
    check_supabase()
    test_thumbnail_sizes()
