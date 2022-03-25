import requests
import json
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tiktok.com/"
}


# ---------------- STEP 1: GET CHALLENGE ID ---------------- #

def get_challenge_id(hashtag):
    url = f"https://www.tiktok.com/tag/{hashtag}"
    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        return None

    import re
    m = re.search(r'"challengeId":"(\d+)"', r.text)
    return m.group(1) if m else None


# ---------------- STEP 2: FETCH VIDEOS ---------------- #

def fetch_videos(challenge_id, max_pages=5):
    videos = []
    cursor = 0

    for _ in range(max_pages):
        url = "https://www.tiktok.com/api/challenge/item_list/"

        params = {
            "challengeID": challenge_id,
            "count": 30,
            "cursor": cursor
        }

        r = requests.get(url, headers=HEADERS, params=params)

        if r.status_code != 200:
            break

        data = r.json()

        for item in data.get("itemList", []):
            stats = item.get("stats", {})
            author = item.get("author", {})

            videos.append({
                "video_id": item.get("id"),
                "author": author.get("uniqueId"),
                "description": item.get("desc"),
                "create_time": item.get("createTime"),
                "likes": stats.get("diggCount"),
                "comments": stats.get("commentCount"),
                "shares": stats.get("shareCount"),
                "views": stats.get("playCount")
            })

        if not data.get("hasMore"):
            break

        cursor = data.get("cursor")
        time.sleep(1)  # avoid blocking

    return videos


# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    hashtag = "ai"

    challenge_id = get_challenge_id(hashtag)

    if not challenge_id:
        print("Failed to get challenge ID")
    else:
        videos = fetch_videos(challenge_id, max_pages=10)

        print(f"Collected {len(videos)} videos")

        for v in videos[:5]:
            print(v)
