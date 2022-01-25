import requests
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json"
}


def extract_slug(url):
    return url.rstrip("/").split("/")[-1]


def fetch_top_answer(slug):
    url = "https://www.quora.com/graphql/gql_para_POST"

    payload = {
        "queryName": "QuestionAnswersListQuery",
        "variables": {
            "questionSlug": slug,
            "first": 1
        },
        "extensions": {
            "hash": "de1d9c7d7f3f9e6d5c5c9f1f4f9d3e5c"
        }
    }

    r = requests.post(url, headers=HEADERS, data=json.dumps(payload))

    if r.status_code != 200:
        return None

    try:
        data = r.json()
        answer = data["data"]["question"]["answers"]["edges"][0]["node"]["content"]
        return clean_html(answer)
    except:
        return None


def clean_html(html):
    return re.sub("<.*?>", "", html).strip()


if __name__ == "__main__":
    url = "https://www.quora.com/What-is-data-engineering"

    slug = extract_slug(url)
    answer = fetch_top_answer(slug)

    print(answer if answer else "No answer found")
