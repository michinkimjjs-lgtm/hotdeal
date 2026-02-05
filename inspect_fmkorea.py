import requests

url = "https://www.fmkorea.com/hotdeal"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Referer': 'https://www.fmkorea.com/'
}

res = requests.get(url, headers=headers)
with open("fmkorea_list.html", "w", encoding="utf-8") as f:
    f.write(res.text)

print("Saved fmkorea_list.html")
