import requests
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch(url):
    r = requests.get(url, headers=HEADERS)
    return r.text if r.status_code == 200 else ""


def extract_profile_data(html):
    m = re.search(r'<script id="SIGI_STATE" type="application/json">(.*?)</script>', html)

    if not m:
        return {}

    try:
        data = json.loads(m.group(1))
    except:
        return {}

    try:
        user = list(data["UserModule"]["users"].values())[0]
        stats = list(data["UserModule"]["stats"].values())[0]

        return {
            "username": user.get("uniqueId"),
            "nickname": user.get("nickname"),
            "bio": user.get("signature"),
            "verified": user.get("verified"),
            "followers": stats.get("followerCount"),
            "following": stats.get("followingCount"),
            "likes": stats.get("heartCount"),
            "videos": stats.get("videoCount")
        }
    except:
        return {}


if __name__ == "__main__":
    profile_url = "https://www.tiktok.com/@username"

    html = fetch(profile_url)
    profile = extract_profile_data(html)

    for k, v in profile.items():
        print(f"{k}: {v}")
