import requests
from collections import defaultdict

BEARER_TOKEN = "YOUR_BEARER_TOKEN"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}


# ---------------- HELPERS ---------------- #

def extract_tweet_id(url):
    return url.rstrip("/").split("/")[-1]


# ---------------- FETCH ---------------- #

def fetch_conversation(tweet_id, max_pages=10):
    url = "https://api.twitter.com/2/tweets/search/recent"

    query = f"conversation_id:{tweet_id}"

    tweets = []
    next_token = None

    for _ in range(max_pages):
        params = {
            "query": query,
            "max_results": 100,
            "tweet.fields": "author_id,conversation_id,created_at,referenced_tweets"
        }

        if next_token:
            params["next_token"] = next_token

        r = requests.get(url, headers=HEADERS, params=params)

        if r.status_code != 200:
            break

        data = r.json()
        tweets.extend(data.get("data", []))

        next_token = data.get("meta", {}).get("next_token")
        if not next_token:
            break

    return tweets


# ---------------- BUILD TREE ---------------- #

def build_tree(tweets, root_id):
    children = defaultdict(list)
    tweet_map = {}

    for t in tweets:
        tweet_map[t["id"]] = t

    for t in tweets:
        parent_id = None

        refs = t.get("referenced_tweets", [])
        for ref in refs:
            if ref["type"] == "replied_to":
                parent_id = ref["id"]

        if parent_id:
            children[parent_id].append(t["id"])

    return tweet_map, children


# ---------------- PRINT TREE ---------------- #

def print_tree(root_id, tweet_map, children, level=0):
    tweet = tweet_map.get(root_id)
    if not tweet:
        return

    indent = "  " * level
    print(f"{indent}- {tweet['text'][:80]}")

    for child_id in children.get(root_id, []):
        print_tree(child_id, tweet_map, children, level + 1)


# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    tweet_url = "https://twitter.com/user/status/1234567890"

    root_id = extract_tweet_id(tweet_url)

    tweets = fetch_conversation(root_id)

    tweet_map, children = build_tree(tweets, root_id)

    print("\nConversation Tree:\n")
    print_tree(root_id, tweet_map, children)
