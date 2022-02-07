import requests
import json
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json"
}

GRAPHQL_URL = "https://www.quora.com/graphql/gql_para_POST"
HASH = "de1d9c7d7f3f9e6d5c5c9f1f4f9d3e5c"


def extract_username(url):
    return url.rstrip("/").split("/")[-1]


def clean_html(html):
    return re.sub("<.*?>", "", html).strip()


def fetch_page(username, cursor=None, limit=20):
    payload = {
        "queryName": "UserProfileAnswersQuery",
        "variables": {
            "username": username,
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
        data = r.json()["data"]["user"]["answers"]
    except:
        return [], None, False

    answers = []

    for edge in data.get("edges", []):
        node = edge.get("node", {})

        answers.append({
            "question": node.get("question", {}).get("title"),
            "votes": node.get("upvoteCount"),
            "answer": clean_html(node.get("content", "")),
            "created": node.get("creationTime")
        })

    page_info = data.get("pageInfo", {})
    return answers, page_info.get("endCursor"), page_info.get("hasNextPage")


def fetch_all_answers(username, cursor=None, collected=None):
    if collected is None:
        collected = []

    answers, next_cursor, has_next = fetch_page(username, cursor)

    if not answers:
        return collected

    collected.extend(answers)

    if has_next and next_cursor:
        return fetch_all_answers(username, next_cursor, collected)

    return collected


if __name__ == "__main__":
    profile_url = "https://www.quora.com/profile/SomeUser"

    username = extract_username(profile_url)
    answers = fetch_all_answers(username)

    for i, a in enumerate(answers, 1):
        print(f"{i}. {a['question']} | Votes: {a['votes']}")
        print(a["answer"][:300])
        print("-" * 80)
