import requests
import json
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json"
}


def extract_slug(url):
    return url.rstrip("/").split("/")[-1]


def clean_html(html):
    return re.sub("<.*?>", "", html).strip()


def fetch_answers(slug, limit=20):
    url = "https://www.quora.com/graphql/gql_para_POST"

    cursor = None
    has_next = True
    results = []

    while has_next:
        payload = {
            "queryName": "QuestionAnswersListQuery",
            "variables": {
                "questionSlug": slug,
                "first": limit,
                "after": cursor
            },
            "extensions": {
                "hash": "de1d9c7d7f3f9e6d5c5c9f1f4f9d3e5c"
            }
        }

        r = requests.post(url, headers=HEADERS, data=json.dumps(payload))
        if r.status_code != 200:
            break

        try:
            data = r.json()["data"]["question"]["answers"]
        except:
            break

        for edge in data["edges"]:
            node = edge["node"]

            results.append({
                "author": node.get("author", {}).get("name"),
                "votes": node.get("upvoteCount"),
                "answer": clean_html(node.get("content", "")),
                "created": node.get("creationTime")
            })

        page_info = data.get("pageInfo", {})
        has_next = page_info.get("hasNextPage")
        cursor = page_info.get("endCursor")

        if not has_next:
            break

    return results


if __name__ == "__main__":
    url = "https://www.quora.com/What-is-data-engineering"

    slug = extract_slug(url)
    answers = fetch_answers(slug)

    for i, a in enumerate(answers, 1):
        print(f"{i}. {a['author']} | Votes: {a['votes']}")
        print(a["answer"][:300])
        print("-" * 80)
