import requests
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch(url):
    r = requests.get(url, headers=HEADERS)
    return r.text if r.status_code == 200 else ""


def extract_json(html):
    m = re.search(r'<script id="SIGI_STATE" type="application/json">(.*?)</script>', html)
    return json.loads(m.group(1)) if m else {}


def extract_videos(data, limit=30):
    videos = []

    try:
        items = data["ItemModule"]
    except:
        return videos

    count = 0

    for vid, v in items.items():
        if count >= limit:
            break

        stats = v.get("stats", {})
        author = v.get("author")

        videos.append({
            "video_id": vid,
            "author": author,
            "description": v.get("desc"),
            "create_time": v.get("createTime"),
            "likes": stats.get("diggCount"),
            "comments": stats.get("commentCount"),
            "shares": stats.get("shareCount"),
            "views": stats.get("playCount")
        })

        count += 1

    return videos


if __name__ == "__main__":
    profile_url = "https://www.tiktok.com/@username"

    html = fetch(profile_url)
    data = extract_json(html)

    videos = extract_videos(data, limit=30)

    for v in videos:
        print(v)
