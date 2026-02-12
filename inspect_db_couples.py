
import os
from supabase import create_client

URL = "https://zvlntvovzffizoruwxqx.supabase.co"
KEY = "sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV"
supabase = create_client(URL, KEY)

def inspect_deal(keyword):
    print(f"--- Searching for '{keyword}' ---")
    res = supabase.table("hotdeals").select("*").ilike("title", f"%{keyword}%").limit(1).execute()
    if res.data:
        deal = res.data[0]
        print(f"Title: {deal['title']}")
        print(f"Source: {deal['source']}")
        print(f"Content Preview (First 500 chars):")
        print(deal.get('content', '')[:500])
        
        content = deal.get('content', '')
        if "<!-- BUY_URL:" in content:
            print("\n[SUCCESS] BUY_URL tag FOUND.")
        else:
            print("\n[FAIL] BUY_URL tag NOT found.")
            
        if "<!-- MALL_NAME:" in content:
            print("[SUCCESS] MALL_NAME tag FOUND.")
        else:
            print("[FAIL] MALL_NAME tag NOT found.")
    else:
        print("No deal found.")

if __name__ == "__main__":
    inspect_deal("자연별곡") # From screenshot
    inspect_deal("코카콜라") # From screenshot
