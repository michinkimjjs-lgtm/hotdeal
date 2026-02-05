from supabase import create_client
URL = 'https://zvlntvovzffizoruwxqx.supabase.co'
KEY = 'sb_publishable_QQaxPklEyj2C7IVhtmspMg_AQmHkQKV'
s = create_client(URL, KEY)
res = s.table('hotdeals').select('title, img_url').eq('source', 'Ruliweb').limit(10).execute()
for r in res.data:
    print(f"Title: {r['title'][:30]}")
    print(f"IMG: {r['img_url']}")
    print("-" * 20)
