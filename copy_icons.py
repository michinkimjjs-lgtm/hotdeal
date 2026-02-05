import shutil
import os

# Origin paths from brain artifacts
brain_dir = r"C:\Users\michi\.gemini\antigravity\brain\9d859d00-afba-4411-b735-bff96d6048e6"
assets_dir = r"e:\an\Hot\assets"

files_to_copy = {
    "fmkorea_icon_1770178632763.png": "fmkorea_icon.png",
    "ppomppu_icon_1770178649014.png": "ppomppu_icon.png",
    "ruliweb_icon_new_1770183065484.png": "ruliweb_icon.png"
}

for src_name, dst_name in files_to_copy.items():
    src_path = os.path.join(brain_dir, src_name)
    dst_path = os.path.join(assets_dir, dst_name)
    try:
        shutil.copy2(src_path, dst_path)
        print(f"Success: {dst_name} copied.")
    except Exception as e:
        print(f"Error copying {dst_name}: {e}")
