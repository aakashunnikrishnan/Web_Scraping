import requests

BEARER_TOKEN = "YOUR_BEARER_TOKEN"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}


def get_user_id(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    r = requests.get(url, headers=HEADERS)

    if r.status_code != 200:
        print("Error fetching user:", r.text)
        return None

    return r.json().get("data", {}).get("id")


def get_user_tweets(user_id, max_results=10, pagination_token=None):
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"

    params = {
        "max_results": max_results,
        "tweet.fields": "created_at,public_metrics"
    }

    if pagination_token:
        params["pagination_token"] = pagination_token

    r = requests.get(url, headers=HEADERS, params=params)

    if r.status_code != 200:
        print("Error fetching tweets:", r.text)
        return [], None

    data = r.json()

    tweets = []
    for t in data.get("data", []):
        tweets.append({
            "id": t.get("id"),
            "text": t.get("text"),
            "created_at": t.get("created_at"),
            "likes": t.get("public_metrics", {}).get("like_count"),
            "retweets": t.get("public_metrics", {}).get("retweet_count"),
            "replies": t.get("public_metrics", {}).get("reply_count")
        })

    next_token = data.get("meta", {}).get("next_token")
    return tweets, next_token


def fetch_all_tweets(username, max_pages=3):
    user_id = get_user_id(username)
    if not user_id:
        return []

    all_tweets = []
    token = None

    for _ in range(max_pages):
        tweets, token = get_user_tweets(user_id, max_results=100, pagination_token=token)

        if not tweets:
            break

        all_tweets.extend(tweets)

        if not token:
            break

    return all_tweets


if __name__ == "__main__":
    username = "elonmusk"

    tweets = fetch_all_tweets(username, max_pages=5)

    for t in tweets:
        print(f"{t['created_at']} | {t['text']}")
        print(f"Likes: {t['likes']} RT: {t['retweets']}")
        print("-" * 80)
