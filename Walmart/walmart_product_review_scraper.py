import requests
import csv
import re
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}


def fetch(url):
    r = requests.get(url, headers=HEADERS)
    return r.text if r.status_code == 200 else ""


def extract_product_meta(html):
    m = re.search(r'window\.__WML_REDUX_INITIAL_STATE__\s*=\s*({.*?});', html)
    if not m:
        return {}

    try:
        data = json.loads(m.group(1))
        product = data.get("product", {}).get("product", {})

        return {
            "product_name": product.get("name"),
            "rating": product.get("averageRating"),
            "rating_count": product.get("numberOfReviews"),
            "review_count": product.get("numberOfReviews"),
            "price": product.get("price", {}).get("price")
        }
    except:
        return {}


def extract_product_id(url):
    m = re.search(r"/ip/.*?/(\d+)", url)
    return m.group(1) if m else None


def fetch_reviews(product_id, page=1):
    url = f"https://www.walmart.com/reviews/product/{product_id}?page={page}"
    html = fetch(url)

    m = re.search(r'window\.__WML_REDUX_INITIAL_STATE__\s*=\s*({.*?});', html)
    if not m:
        return []

    try:
        data = json.loads(m.group(1))
        reviews = data.get("reviews", {}).get("reviews", [])
    except:
        return []

    results = []

    for r in reviews:
        results.append({
            "review": r.get("reviewText"),
            "author": r.get("reviewer"),
            "rating": r.get("rating"),
            "date": r.get("submissionTime")
        })

    return results


def read_input(file):
    urls = []
    with open(file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            urls.append(row["url"])
    return urls


def write_output(file, rows):
    fields = [
        "input_link", "product_name", "rating", "rating_count",
        "review_count", "price", "review", "author", "date", "place"
    ]
    with open(file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def crawl(input_csv, output_csv, max_pages=3):
    urls = read_input(input_csv)
    final = []

    for url in urls:
        html = fetch(url)
        if not html:
            continue

        meta = extract_product_meta(html)
        product_id = extract_product_id(url)

        if not product_id:
            continue

        for page in range(1, max_pages + 1):
            reviews = fetch_reviews(product_id, page)

            if not reviews:
                break

            for r in reviews:
                final.append({
                    "input_link": url,
                    "product_name": meta.get("product_name"),
                    "rating": meta.get("rating"),
                    "rating_count": meta.get("rating_count"),
                    "review_count": meta.get("review_count"),
                    "price": meta.get("price"),
                    "review": r.get("review"),
                    "author": r.get("author"),
                    "date": r.get("date"),
                    "place": product_id
                })

    write_output(output_csv, final)


if __name__ == "__main__":
    crawl("input.csv", "output.csv", max_pages=5)
