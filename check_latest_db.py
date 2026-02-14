
import os
import sys
from supabase import create_client, Client
from datetime import datetime, timedelta

# Supabase Credentials (Public)
SUPABASE_URL = "https://zvlntvovzffizoruwxqx.supabase.co"
SUPABASE_KEY = "sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV"

def main():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    try:
        # Fetch latest 5 items ordered by created_at desc
        response = supabase.table("hotdeals") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(5) \
            .execute()
            
        data = response.data
        if not data:
            print("No data found.")
            return

        print(f"Checking latest {len(data)} items:")
        now = datetime.utcnow()
        
        for item in data:
            created_at = item.get('created_at')
            title = item.get('title')
            source = item.get('source')
            
            # Simple parsing (ISO format usually)
            # created_at is likely UTC string
            try:
                # 2024-02-13T06:21:55.123456 or similar
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                diff = now - dt.replace(tzinfo=None)
                minutes_ago = int(diff.total_seconds() / 60)
                
                safe_title = title.encode('cp949', 'ignore').decode('cp949')
                print(f"- [{source}] {safe_title[:30]}... | {minutes_ago}m ago (DB: {created_at})")
            except Exception as e:
                print(f"- [{source}] {title[:30]}... | 시간 파싱 에러 ({created_at})")

    except Exception as e:
        print(f"DB Fetch Error: {e}")

if __name__ == "__main__":
    main()
