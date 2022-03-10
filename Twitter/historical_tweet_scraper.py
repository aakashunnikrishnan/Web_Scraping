import snscrape.modules.twitter as sntwitter
import csv


def scrape_tweets(query, start_date, end_date, max_tweets=500):
    tweets = []

    search_query = f"{query} since:{start_date} until:{end_date}"

    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(search_query).get_items()):
        if i >= max_tweets:
            break

        tweets.append({
            "date": tweet.date,
            "id": tweet.id,
            "content": tweet.content,
            "username": tweet.user.username,
            "likes": tweet.likeCount,
            "retweets": tweet.retweetCount,
            "replies": tweet.replyCount
        })

    return tweets


def write_csv(file, rows):
    fields = ["date", "id", "username", "content", "likes", "retweets", "replies"]

    with open(file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    query = "election"
    start_date = "2020-11-03"
    end_date = "2020-11-04"

    tweets = scrape_tweets(query, start_date, end_date, max_tweets=500)

    print(f"Collected {len(tweets)} tweets")

    write_csv("tweets.csv", tweets)
