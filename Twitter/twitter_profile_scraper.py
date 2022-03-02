import requests
import csv

BEARER_TOKEN = "YOUR_BEARER_TOKEN"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}


# ---------------- GET USER ID ---------------- #

def get_user_id(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"

    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        return None

    return r.json().get("data", {}).get("id")


# ---------------- FETCH FOLLOWERS / FOLLOWING ---------------- #

def fetch_users(user_id, mode="followers", max_pages=5):
    if mode == "followers":
        url = f"https://api.twitter.com/2/users/{user_id}/followers"
    else:
        url = f"https://api.twitter.com/2/users/{user_id}/following"

    users = []
    next_token = None

    for _ in range(max_pages):
        params = {
            "max_results": 1000,
            "user.fields": "username,name,description,public_metrics,created_at"
        }

        if next_token:
            params["pagination_token"] = next_token

        r = requests.get(url, headers=HEADERS, params=params)

        if r.status_code != 200:
            break

        data = r.json()

        for u in data.get("data", []):
            users.append({
                "username": u.get("username"),
                "name": u.get("name"),
                "bio": u.get("description"),
                "followers": u.get("public_metrics", {}).get("followers_count"),
                "following": u.get("public_metrics", {}).get("following_count"),
                "tweet_count": u.get("public_metrics", {}).get("tweet_count"),
                "account_created": u.get("created_at")
            })

        next_token = data.get("meta", {}).get("next_token")
        if not next_token:
            break

    return users


# ---------------- WRITE CSV ---------------- #

def write_csv(file, rows):
    fields = [
        "username", "name", "bio",
        "followers", "following", "tweet_count", "account_created"
    ]

    with open(file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    username = "elonmusk"
    mode = "followers"   # or "following"

    user_id = get_user_id(username)

    if user_id:
        users = fetch_users(user_id, mode=mode, max_pages=10)

        print(f"Collected {len(users)} users")

        write_csv("output.csv", users)
