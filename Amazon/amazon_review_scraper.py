import requests
import re
import csv
import time
import random
import argparse
import sys


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "DNT": "1",
}


def get_headers():
    return {**HEADERS, "User-Agent": random.choice(USER_AGENTS)}


def extract_asin(url):
    match = re.search(r"/(?:dp|gp/product)/([A-Z0-9]{10})", url)
    if not match:
        print("Could not extract ASIN from URL.")
        sys.exit(1)
    return match.group(1)


def fetch(url, session, retries=3):
    for attempt in range(1, retries + 1):
        try:
            r = session.get(url, headers=get_headers(), timeout=15)
            if r.status_code == 200:
                return r.text
            print(f"HTTP {r.status_code} (attempt {attempt}/{retries})")
        except requests.RequestException as e:
            print(f"Request error (attempt {attempt}/{retries}): {e}")
        if attempt < retries:
            time.sleep(random.uniform(3, 7))
    return None


def clean(text):
    return re.sub(r'\s+', ' ', text).strip()


def extract_between(pattern, html, default="N/A"):
    match = re.search(pattern, html, re.DOTALL)
    return clean(re.sub(r'<[^>]+>', '', match.group(1))) if match else default


def parse_reviews(html):
    reviews = []
    blocks = re.findall(r'<div[^>]+data-hook="review"[^>]*>(.*?)</div>\s*</div>\s*</div>\s*</div>', html, re.DOTALL)

    for block in blocks:
        name = extract_between(r'class="a-profile-name"[^>]*>(.*?)</span>', block)

        rating_raw = extract_between(r'data-hook="review-star-rating"[^>]*>.*?<span[^>]*>(.*?)</span>', block)
        rating_match = re.search(r'([\d.]+) out of', rating_raw)
        rating = rating_match.group(1) if rating_match else "N/A"

        title = extract_between(r'data-hook="review-title"[^>]*>.*?<span[^>]*>(.*?)</span>', block)
        date = extract_between(r'data-hook="review-date"[^>]*>(.*?)</span>', block)
        verified = "Yes" if 'data-hook="avp-badge"' in block else "No"
        helpful = extract_between(r'data-hook="helpful-vote-statement"[^>]*>(.*?)</span>', block, "0")
        body = extract_between(r'data-hook="review-body"[^>]*>.*?<span[^>]*>(.*?)</span>', block)

        reviews.append({
            "reviewer_name": name,
            "rating": rating,
            "title": title,
            "date": date,
            "verified_purchase": verified,
            "helpful_votes": helpful,
            "review_body": body,
        })

    return reviews


def has_next_page(html):
    return bool(re.search(r'class="a-last"[^>]*>.*?<a\s+href=', html, re.DOTALL))


def save_csv(reviews, filepath):
    fields = ["reviewer_name", "rating", "title", "date", "verified_purchase", "helpful_votes", "review_body"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(reviews)
    print(f"Saved {len(reviews)} reviews to '{filepath}'")


def print_reviews(reviews):
    for i, r in enumerate(reviews, 1):
        print(f"\n{'─' * 60}")
        print(f"Review #{i}")
        print(f"  Reviewer : {r['reviewer_name']}")
        print(f"  Rating   : {r['rating']} / 5")
        print(f"  Title    : {r['title']}")
        print(f"  Date     : {r['date']}")
        print(f"  Verified : {r['verified_purchase']}")
        print(f"  Helpful  : {r['helpful_votes']}")
        print(f"  Body     : {r['review_body'][:300]}{'...' if len(r['review_body']) > 300 else ''}")


def scrape_reviews(product_url, max_pages=5, output_file=None):
    asin = extract_asin(product_url)
    print(f"ASIN: {asin}")

    session = requests.Session()
    all_reviews = []

    for page in range(1, max_pages + 1):
        url = f"https://www.amazon.com/product-reviews/{asin}?pageNumber={page}&sortBy=recent&reviewerType=all_reviews"
        print(f"Fetching page {page}/{max_pages}...")

        html = fetch(url, session)
        if not html:
            print(f"Failed to fetch page {page}. Stopping.")
            break

        reviews = parse_reviews(html)
        if not reviews:
            print("No reviews found. Reached end.")
            break

        all_reviews.extend(reviews)
        print(f"  {len(reviews)} reviews found (total: {len(all_reviews)})")

        if not has_next_page(html):
            break

        time.sleep(random.uniform(2, 5))

    print(f"\nTotal reviews scraped: {len(all_reviews)}")

    if output_file:
        save_csv(all_reviews, output_file)
    else:
        print_reviews(all_reviews)

    return all_reviews


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Amazon product URL")
    parser.add_argument("--pages", type=int, default=5)
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()
    scrape_reviews(args.url, max_pages=args.pages, output_file=args.output)


if __name__ == "__main__":
    main()
