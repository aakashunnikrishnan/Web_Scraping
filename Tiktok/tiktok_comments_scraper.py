import requests
import re
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tiktok.com/"
}


# ---------------- STEP 1: EXTRACT VIDEO ID ---------------- #

def extract_video_id(url):
    m = re.search(r"/video/(\d+)", url)
    return m.group(1) if m else None


# ---------------- STEP 2: FETCH COMMENTS ---------------- #

def fetch_comments(video_id, max_pages=10):
    comments = []
    cursor = 0

    for _ in range(max_pages):
        url = "https://www.tiktok.com/api/comment/list/"

        params = {
            "aweme_id": video_id,
            "count": 50,
            "cursor": cursor
        }

        r = requests.get(url, headers=HEADERS, params=params)

        if r.status_code != 200:
            break

        data = r.json()

        for c in data.get("comments", []):
            user = c.get("user", {})

            comments.append({
                "comment_id": c.get("cid"),
                "text": c.get("text"),
                "author": user.get("unique_id"),
                "likes": c.get("digg_count"),
                "replies": c.get("reply_comment_total"),
                "timestamp": c.get("create_time")
            })

        if not data.get("has_more"):
            break

        cursor = data.get("cursor")
        time.sleep(1)

    return comments


# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    video_url = "https://www.tiktok.com/@username/video/1234567890"

    video_id = extract_video_id(video_url)

    if not video_id:
        print("Invalid URL")
    else:
        comments = fetch_comments(video_id, max_pages=20)

        print(f"Collected {len(comments)} comments")

        for c in comments[:5]:
            print(c)
