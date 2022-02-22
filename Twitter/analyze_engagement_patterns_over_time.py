import requests
from datetime import datetime
from collections import defaultdict
import math

BEARER_TOKEN = "YOUR_BEARER_TOKEN"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}


# ---------------- FETCH ---------------- #

def search_tweets(query, max_pages=10):
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


# ---------------- ANALYSIS ---------------- #

def analyze(tweets):
    day_engagement = defaultdict(list)
    hour_engagement = defaultdict(list)

    lengths = []
    likes = []
    retweets = []

    for t in tweets:
        created = datetime.strptime(t["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        day = created.strftime("%A")
        hour = created.hour

        metrics = t["public_metrics"]
        engagement = metrics["like_count"] + metrics["retweet_count"]

        day_engagement[day].append(engagement)
        hour_engagement[hour].append(engagement)

        length = len(t["text"])
        lengths.append(length)
        likes.append(metrics["like_count"])
        retweets.append(metrics["retweet_count"])

    # avg engagement per day
    best_day = max(day_engagement.items(), key=lambda x: avg(x[1]))

    # avg engagement per hour
    best_hour = max(hour_engagement.items(), key=lambda x: avg(x[1]))

    # correlations
    corr_len_likes = correlation(lengths, likes)
    corr_len_retweets = correlation(lengths, retweets)

    return {
        "best_day": best_day,
        "best_hour": best_hour,
        "corr_len_likes": corr_len_likes,
        "corr_len_retweets": corr_len_retweets
    }


def avg(lst):
    return sum(lst) / len(lst) if lst else 0


def correlation(x, y):
    n = len(x)
    if n == 0:
        return 0

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
    den_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
    den_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))

    if den_x * den_y == 0:
        return 0

    return num / (den_x * den_y)


# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    query = "#AI lang:en -is:retweet"

    tweets = search_tweets(query, max_pages=6)  # ~600 tweets

    print(f"Collected: {len(tweets)} tweets")

    result = analyze(tweets)

    print("\nBest Day:")
    print(result["best_day"])

    print("\nBest Hour:")
    print(result["best_hour"])

    print("\nCorrelation (Length vs Likes):", result["corr_len_likes"])
    print("Correlation (Length vs Retweets):", result["corr_len_retweets"])
