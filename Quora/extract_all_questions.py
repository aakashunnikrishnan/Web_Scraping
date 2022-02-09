import requests
import json
import re
import csv

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json"
}

GRAPHQL_URL = "https://www.quora.com/graphql/gql_para_POST"
HASH = "de1d9c7d7f3f9e6d5c5c9f1f4f9d3e5c"


def extract_topic_slug(url):
    return url.rstrip("/").split("/")[-1]


def clean_html(html):
    return re.sub("<.*?>", "", html).strip()


def fetch_topic_questions(topic_slug, cursor=None, limit=20):
    payload = {
        "queryName": "TopicQuestionsListQuery",
        "variables": {
            "topicSlug": topic_slug,
            "first": limit,
            "after": cursor
        },
        "extensions": {
            "hash": HASH
        }
    }

    r = requests.post(GRAPHQL_URL, headers=HEADERS, data=json.dumps(payload))
    if r.status_code != 200:
        return [], None, False

    try:
        data = r.json()["data"]["topic"]["questions"]
    except:
        return [], None, False

    questions = []
    for edge in data.get("edges", []):
        node = edge.get("node", {})
        questions.append({
            "title": node.get("title"),
            "slug": node.get("slug")
        })

    page_info = data.get("pageInfo", {})
    return questions, page_info.get("endCursor"), page_info.get("hasNextPage")


def fetch_top_answer(question_slug):
    payload = {
        "queryName": "QuestionAnswersListQuery",
        "variables": {
            "questionSlug": question_slug,
            "first": 1
        },
        "extensions": {
            "hash": HASH
        }
    }

    r = requests.post(GRAPHQL_URL, headers=HEADERS, data=json.dumps(payload))
    if r.status_code != 200:
        return {}

    try:
        node = r.json()["data"]["question"]["answers"]["edges"][0]["node"]
        return {
            "answer": clean_html(node.get("content", "")),
            "author": node.get("author", {}).get("name"),
            "votes": node.get("upvoteCount")
        }
    except:
        return {}


def crawl(topic_url, output_file="output.csv", pages=3):
    topic_slug = extract_topic_slug(topic_url)

    cursor = None
    all_rows = []

    for _ in range(pages):
        questions, cursor, has_next = fetch_topic_questions(topic_slug, cursor)

        if not questions:
            break

        for q in questions:
            ans = fetch_top_answer(q["slug"])

            all_rows.append({
                "question": q["title"],
                "answer": ans.get("answer"),
                "author": ans.get("author"),
                "votes": ans.get("votes")
            })

        if not has_next:
            break

    write_csv(output_file, all_rows)


def write_csv(path, rows):
    fields = ["question", "answer", "author", "votes"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    topic_url = "https://www.quora.com/topic/Machine-Learning"
    crawl(topic_url, "output.csv", pages=3)
