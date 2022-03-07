import requests
from collections import defaultdict

BEARER_TOKEN = "YOUR_BEARER_TOKEN"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}


# ---------------- HELPERS ---------------- #

def extract_tweet_id(url):
    return url.rstrip("/").split("/")[-1]


# ---------------- FETCH ALL RELATED TWEETS ---------------- #

def fetch_all_related(tweet_id, max_pages=10):
    url = "https://api.twitter.com/2/tweets/search/recent"

    query = f"conversation_id:{tweet_id}"

    tweets = []
    next_token = None

    for _ in range(max_pages):
        params = {
            "query": query,
            "max_results": 100,
            "tweet.fields": "author_id,created_at,referenced_tweets"
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


# ---------------- BUILD RETWEET GRAPH ---------------- #

def build_retweet_graph(tweets, root_id):
    graph = defaultdict(list)
    tweet_map = {}

    for t in tweets:
        tweet_map[t["id"]] = t

    for t in tweets:
        refs = t.get("referenced_tweets", [])

        for ref in refs:
            if ref["type"] == "retweeted":
                parent_id = ref["id"]
                graph[parent_id].append(t["id"])

    return tweet_map, graph


# ---------------- PRINT GRAPH ---------------- #

def print_graph(node_id, tweet_map, graph, level=0, visited=None):
    if visited is None:
        visited = set()

    if node_id in visited:
        return

    visited.add(node_id)

    tweet = tweet_map.get(node_id)
    if not tweet:
        return

    indent = "  " * level
    print(f"{indent}- User:{tweet['author_id']} | {tweet['text'][:60]}")

    for child in graph.get(node_id, []):
        print_graph(child, tweet_map, graph, level + 1, visited)


# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    tweet_url = "https://twitter.com/user/status/1234567890"

    root_id = extract_tweet_id(tweet_url)

    tweets = fetch_all_related(root_id)

    tweet_map, graph = build_retweet_graph(tweets, root_id)

    print("\nRetweet Network:\n")
    print_graph(root_id, tweet_map, graph)
