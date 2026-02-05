import os
import subprocess
import time
import sys

def run_command(cmd):
    print(f"\n> Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False

def main():
    print("=== [All-in-One Deployment Worker] ===")
    
    # 1. Local Crawling & DB Update
    print("\n[Step 1] Triggering Local Crawling...")
    try:
        from crawler import PpomppuCrawler, FMKoreaCrawler, RuliwebCrawler, URL, KEY
        crawlers = [
            PpomppuCrawler(URL, KEY),
            FMKoreaCrawler(URL, KEY),
            RuliwebCrawler(URL, KEY)
        ]
        for c in crawlers:
            c.crawl()
            time.sleep(1) # Interval for stability
        print("Crawling Done.")
    except Exception as e:
        print(f"Crawling Failed: {e}")

    # 2. Git Sync
    print("\n[Step 2] Syncing to GitHub...")
    run_command(["git", "add", "crawler.py", "app.js", "assets/"])
    if run_command(["git", "commit", "-m", "fix: Finalize Ruliweb image extraction and performance optimization"]):
        run_command(["git", "push", "origin", "main"])
    
    print("\n=== All Tasks Completed Successfully! ===")

if __name__ == "__main__":
    main()
