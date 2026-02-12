import os
from supabase import create_client

SUPABASE_URL = 'https://zvlntvovzffizoruwxqx.supabase.co'
SUPABASE_KEY = 'sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV'

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_db():
    print("Connecting to Supabase...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Fetch latest Ruliweb item
    print("Fetching latest Ruliweb item...")
    res = supabase.table("hotdeals").select("*").eq("source", "Ruliweb").order("created_at", desc=True).limit(1).execute()
    
    if res.data:
        item = res.data[0]
        print(f"\nTitle: {item['title']}")
        print(f"Source: {item['source']}")
        print(f"URL: {item['url']}")
        print(f"Content Preview (Start): {item['content'][:100]}")
        
        # Check for MALL_NAME comment
        import re
        match = re.search(r'<!-- MALL_NAME: (.*?) -->', item['content'])
        if match:
             print(f"Found MALL_NAME comment: '{match.group(1)}'")
        else:
             print("MALL_NAME comment NOT found.")
             
        # Test Regex on Title
        title_match = re.search(r'^[\[\(](.+?)[\]\)]', item['title'])
        if title_match:
            print(f"Regex Title Match: '{title_match.group(1)}'")
        else:
            print("Regex Title Match: FAILED")
            
    else:
        print("No Ruliweb items found.")

if __name__ == "__main__":
    check_db()
