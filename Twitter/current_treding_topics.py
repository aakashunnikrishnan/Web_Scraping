import requests

BEARER_TOKEN = "YOUR_BEARER_TOKEN"

headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

def get_trending_hashtags(query="india", max_results=50):
    url = "https://api.twitter.com/2/tweets/search/recent"

    params = {
        "query": f"{query} lang:en -is:retweet",
        "max_results": max_results,
        "tweet.fields": "created_at"
    }

    r = requests.get(url, headers=headers, params=params)
    data = r.json()

    hashtags = {}

    for tweet in data.get("data", []):
        words = tweet["text"].split()
        for w in words:
            if w.startswith("#"):
                hashtags[w] = hashtags.get(w, 0) + 1

    sorted_tags = sorted(hashtags.items(), key=lambda x: x[1], reverse=True)
    return sorted_tags


if __name__ == "__main__":
    trends = get_trending_hashtags("india")

    for tag, count in trends[:10]:
        print(tag, count)
