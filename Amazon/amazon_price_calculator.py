import requests
import csv
import re
from datetime import datetime
from html.parser import HTMLParser

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

class ProductParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.capture_price = False
        self.capture_title = False
        self.price = ""
        self.title = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "span":
            cls = attrs.get("class", "")
            if "a-price-whole" in cls or "a-offscreen" in cls:
                self.capture_price = True

        if tag == "span" and attrs.get("id") == "productTitle":
            self.capture_title = True

    def handle_data(self, data):
        if self.capture_price:
            self.price += data.strip()

        if self.capture_title:
            self.title += data.strip()

    def handle_endtag(self, tag):
        if tag == "span":
            self.capture_price = False
            self.capture_title = False


def fetch(url):
    r = requests.get(url, headers=HEADERS)
    return r.text if r.status_code == 200 else ""


def clean_price(text):
    text = re.sub(r"[^\d.]", "", text)
    return float(text) if text else ""


def extract_product(html):
    parser = ProductParser()
    parser.feed(html)

    return {
        "title": parser.title.strip(),
        "price": clean_price(parser.price)
    }


def track_price(urls, output_file="price_history.csv"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows = []

    for url in urls:
        html = fetch(url)
        if not html:
            continue

        data = extract_product(html)

        rows.append({
            "timestamp": now,
            "url": url,
            "title": data["title"],
            "price": data["price"]
        })

    try:
        with open(output_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "url", "title", "price"])
            if f.tell() == 0:
                writer.writeheader()
            writer.writerows(rows)
    except:
        pass


if __name__ == "__main__":
    product_urls = [
        "https://www.amazon.in/dp/B0XXXXXXX",
        "https://www.amazon.in/dp/B0YYYYYYY"
    ]

    track_price(product_urls)
