from supabase import create_client, Client
import os

URL = "https://zvlntvovzffizoruwxqx.supabase.co"
KEY = "sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV"
supabase = create_client(URL, KEY)

response = supabase.table("hotdeals").select("count", count="exact").eq("source", "Ruliweb").execute()
print(f"Ruliweb deals in DB: {response.count}")

# 최근 수집된 항목 5개 확인
recent = supabase.table("hotdeals").select("title, source, created_at").order("created_at", desc=True).limit(10).execute()
for r in recent.data:
    print(f"[{r['source']}] {r['title'][:30]}... ({r['created_at']})")
