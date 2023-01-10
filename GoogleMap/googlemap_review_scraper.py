import requests
import csv
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def extract_place_id(url):
    m = re.search(r"place/.*?/.*?/(.*?)[/?]", url)
    return m.group(1) if m else None


def fetch_reviews(place_id):
    url = "https://www.google.com/maps/preview/review/listentitiesreview"

    params = {
        "pb": f"!1m2!1s{place_id}!2s0!3m1!2i20!4e0"
    }

    r = requests.get(url, headers=HEADERS, params=params)

    if r.status_code != 200:
        return []

    try:
        text = r.text
        json_str = text.split("\n")[1]
        data = json.loads(json_str)
    except:
        return []

    reviews = []

    try:
        for item in data[2]:
            review = {
                "author": item[0][1],
                "rating": item[4],
                "review": item[3],
                "date": item[1]
            }
            reviews.append(review)
    except:
        pass

    return reviews


def fetch_place_name(url):
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        return ""

    m = re.search(r"<title>(.*?)</title>", r.text)
    return m.group(1).replace(" - Google Maps", "") if m else ""


def read_input(file):
    urls = []
    with open(file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            urls.append(row["url"])
    return urls


def write_output(file, rows):
    fields = ["input_link", "place_name", "rating", "review", "author", "date", "place"]
    with open(file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def crawl(file_in, file_out):
    urls = read_input(file_in)
    output = []

    for url in urls:
        place_id = extract_place_id(url)
        if not place_id:
            continue

        place_name = fetch_place_name(url)
        reviews = fetch_reviews(place_id)

        for r in reviews:
            output.append({
                "input_link": url,
                "place_name": place_name,
                "rating": r["rating"],
                "review": r["review"],
                "author": r["author"],
                "date": r["date"],
                "place": place_id
            })

    write_output(file_out, output)


if __name__ == "__main__":
    crawl("input.csv", "output.csv")
