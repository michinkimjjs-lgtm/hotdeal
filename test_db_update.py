from supabase import create_client
import os

URL = "https://zvlntvovzffizoruwxqx.supabase.co"
KEY = "sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV"

def test_update():
    supabase = create_client(URL, KEY)
    
    # 1. Get a recent deal
    res = supabase.table("hotdeals").select("*").limit(1).execute()
    if not res.data:
        print("No deals found to update.")
        return

    deal = res.data[0]
    print(f"Target Deal: {deal['id']} - {deal['title']}")

    # 2. Update content
    update_data = {"content": "<p>Test Content Update by Debugger</p>"}
    
    try:
        # Using upsert or update. Since ID exists, upsert or update by ID works.
        # Let's try update on specific ID to be sure.
        res_update = supabase.table("hotdeals").update(update_data).eq("id", deal['id']).execute()
        print(f"Update Result: {res_update}")
        
        # 3. Verify
        res_check = supabase.table("hotdeals").select("content").eq("id", deal['id']).single().execute()
        print(f"Verified Content: {res_check.data.get('content')}")
        
    except Exception as e:
        print(f"Update Failed: {e}")

if __name__ == "__main__":
    test_update()
