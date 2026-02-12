from crawler import FMKoreaCrawler, URL, KEY
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

def run_real_single_force():
    print("=== Force Refreshing 1 FMKorea Deal ===")
    
    crawler = FMKoreaCrawler(URL, KEY)
    
    # 1. Fetch list to get the latest URL
    print("Fetching list to identify target...")
    html = crawler.fetch_page("https://www.fmkorea.com/hotdeal", encoding='auto')
    if not html:
        print("Failed to fetch list.")
        return

    import re
    # Extract first deal link
    match = re.search(r'class="hotdeal_var8" href="(/[^"]+)"', html)
    if not match:
         match = re.search(r'class="li".*?<a href="(/[^"]+)"', html, re.DOTALL)
         
    target_url = ""
    if match:
        target_url = "https://www.fmkorea.com" + match.group(1)
        print(f"Target URL: {target_url}")
        
        # 2. Delete existing record to force clean insert
        print(f"Deleting existing record for {target_url}...")
        try:
             crawler.supabase.table("hotdeals").delete().eq("url", target_url).execute()
             print("Deleted (if existed).")
        except Exception as e:
             print(f"Delete failed (might not exist): {e}")
             
    # 3. Crawl
    print("Crawling...")
    crawler.crawl(limit=1)

if __name__ == "__main__":
    run_real_single_force()
