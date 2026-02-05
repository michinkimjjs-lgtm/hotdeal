import os
import shutil
import subprocess

# 1. Paths
brain_dir = r"C:\Users\michi\.gemini\antigravity\brain\9d859d00-afba-4411-b735-bff96d6048e6"
project_dir = r"e:\an\Hot"
assets_dir = os.path.join(project_dir, "assets")

# 2. Copy Icons Safely
icons = {
    "fmkorea_icon_1770178632763.png": "fmkorea_icon.png",
    "ppomppu_icon_1770178649014.png": "ppomppu_icon.png",
    "ruliweb_icon_new_1770183065484.png": "ruliweb_icon.png"
}

print("--- Copying Icons ---")
for src, dst in icons.items():
    src_path = os.path.join(brain_dir, src)
    dst_path = os.path.join(assets_dir, dst)
    try:
        shutil.copy2(src_path, dst_path)
        print(f"Copied: {dst}")
    except Exception as e:
        print(f"Error {dst}: {e}")

# 3. Git Push
print("\n--- Pushing to GitHub ---")
try:
    os.chdir(project_dir)
    subprocess.run(["git", "add", "assets", "crawler.py", "app.js"], check=True)
    subprocess.run(["git", "commit", "-m", "fix: Final emergency branding and extraction fix"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("GitHub Push Success!")
except Exception as e:
    print(f"Git Error: {e}")

# 4. Local Crawl for immediate DB update
print("\n--- Running Local Crawl ---")
try:
    from crawler import RuliwebCrawler, URL, KEY
    c = RuliwebCrawler(URL, KEY)
    c.crawl()
    print("Local Crawl Success!")
except Exception as e:
    print(f"Crawl Error: {e}")

print("\n--- ALL TASKS DONE ---")
