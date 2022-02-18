import requests

BEARER_TOKEN = "YOUR_BEARER_TOKEN"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}


def search_tweets(query, max_results=10):
    url = "https://api.twitter.com/2/tweets/search/recent"

    params = {
        "query": query,
        "max_results": max_results,
        "tweet.fields": "author_id,created_at,public_metrics"
    }

    r = requests.get(url, headers=HEADERS, params=params)

    if r.status_code != 200:
        print("Error:", r.text)
        return []

    data = r.json()

    results = []

    for tweet in data.get("data", []):
        results.append({
            "id": tweet.get("id"),
            "text": tweet.get("text"),
            "author_id": tweet.get("author_id"),
            "created_at": tweet.get("created_at"),
            "likes": tweet.get("public_metrics", {}).get("like_count"),
            "retweets": tweet.get("public_metrics", {}).get("retweet_count"),
            "replies": tweet.get("public_metrics", {}).get("reply_count")
        })

    return results


if __name__ == "__main__":
    keyword = "data engineering"

    tweets = search_tweets(keyword, max_results=20)

    for t in tweets:
        print(f"ID: {t['id']}")
        print(f"Text: {t['text']}")
        print(f"Likes: {t['likes']} | RT: {t['retweets']} | Replies: {t['replies']}")
        print("-" * 80)
