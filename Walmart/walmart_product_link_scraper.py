import requests
import csv
import re
import json
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html"
}


def fetch(url):
    r = requests.get(url, headers=HEADERS)
    return r.text if r.status_code == 200 else ""


def extract_state(html):
    m = re.search(r'window\.__WML_REDUX_INITIAL_STATE__\s*=\s*({.*?});', html)
    if not m:
        return {}

    try:
        return json.loads(m.group(1))
    except:
        return {}


def extract_products(state, base_url):
    results = []

    try:
        items = state["searchResult"]["itemStacks"][0]["items"]
    except:
        return results

    for item in items:
        if item.get("usItemId") is None:
            continue

        name = item.get("name")
        product_id = item.get("usItemId")

        link = item.get("canonicalUrl")
        if link:
            link = urljoin(base_url, link)

        price = None
        try:
            price = item.get("priceInfo", {}).get("currentPrice", {}).get("price")
        except:
            pass

        rating = item.get("averageRating")
        rating_count = item.get("numberOfReviews")
        comment_count = item.get("numberOfReviews")

        results.append({
            "productname": name,
            "link": link,
            "skuid": product_id,
            "price": price,
            "rating": rating,
            "rating_count": rating_count,
            "comment_count": comment_count
        })

    return results


def get_next_page_url(url, page):
    if "page=" in url:
        return re.sub(r"page=\d+", f"page={page}", url)
    else:
        return f"{url}&page={page}"


def read_input(file):
    urls = []
    with open(file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            urls.append(row["url"])
    return urls


def write_output(file, rows):
    fields = [
        "productname", "link", "skuid",
        "price", "rating", "rating_count", "comment_count"
    ]
    with open(file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def crawl(input_csv, output_csv, max_pages=5):
    base = "https://www.walmart.com"
    urls = read_input(input_csv)

    final = []

    for url in urls:
        for page in range(1, max_pages + 1):
            page_url = get_next_page_url(url, page)

            html = fetch(page_url)
            if not html:
                break

            state = extract_state(html)
            products = extract_products(state, base)

            if not products:
                break

            final.extend(products)

    write_output(output_csv, final)


if __name__ == "__main__":
    crawl("input.csv", "output.csv", max_pages=10)
