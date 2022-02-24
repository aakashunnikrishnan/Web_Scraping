import requests
from datetime import datetime
from collections import defaultdict
import re

BEARER_TOKEN = "YOUR_BEARER_TOKEN"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}


# ---------------- FETCH ---------------- #

def fetch_tweets(query, max_pages=6):
    url = "https://api.twitter.com/2/tweets/search/recent"

    tweets = []
    next_token = None

    for _ in range(max_pages):
        params = {
            "query": query,
            "max_results": 100,
            "tweet.fields": "created_at,public_metrics"
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


# ---------------- SENTIMENT ---------------- #

positive_words = {
    "good","great","awesome","amazing","love","excellent","best","fantastic","happy","like","super"
}

negative_words = {
    "bad","worst","terrible","awful","hate","poor","disappointing","slow","bug","issue","problem"
}


def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-z\s]", "", text)
    return text


def get_sentiment(text):
    words = clean_text(text).split()

    pos = sum(1 for w in words if w in positive_words)
    neg = sum(1 for w in words if w in negative_words)

    if pos > neg:
        return "positive"
    elif neg > pos:
        return "negative"
    return "neutral"


# ---------------- ANALYSIS ---------------- #

def analyze_sentiment(tweets):
    counts = defaultdict(int)
    engagement_by_sentiment = defaultdict(list)

    for t in tweets:
        sentiment = get_sentiment(t["text"])

        metrics = t["public_metrics"]
        engagement = metrics["like_count"] + metrics["retweet_count"]

        counts[sentiment] += 1
        engagement_by_sentiment[sentiment].append(engagement)

    result = {}

    for k in counts:
        avg_eng = (
            sum(engagement_by_sentiment[k]) / len(engagement_by_sentiment[k])
            if engagement_by_sentiment[k] else 0
        )

        result[k] = {
            "count": counts[k],
            "avg_engagement": avg_eng
        }

    return result


# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    query = "iphone 15 lang:en -is:retweet"

    tweets = fetch_tweets(query, max_pages=6)  # ~500+

    print(f"Collected {len(tweets)} tweets")

    sentiment_result = analyze_sentiment(tweets)

    print("\nSentiment Analysis:")
    for k, v in sentiment_result.items():
        print(f"{k.upper()}: Count={v['count']} AvgEngagement={v['avg_engagement']:.2f}")
