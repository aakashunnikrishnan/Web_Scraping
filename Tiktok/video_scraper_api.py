import requests
import re
import json
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tiktok.com/"
}


# ---------------- STEP 1: GET secUid ---------------- #

def get_secuid(profile_url):
    html = requests.get(profile_url, headers=HEADERS).text

    m = re.search(r'"secUid":"(.*?)"', html)
    return m.group(1) if
