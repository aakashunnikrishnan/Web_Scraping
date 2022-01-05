import requests
import csv
import re
from urllib.parse import urljoin
from html.parser import HTMLParser

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

class AmazonParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.products = []
        self.current = {}
        self.capture_title = False
        self.capture_price = False
        self.capture_original = False
        self.capture_rating = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "div" and attrs.get("data-component-type") == "s-search-result":
            self.current = {"name": "", "price": "", "original_price": "", "rating": "", "link": "", "id": attrs.get("data-asin")}

        if not self.current:
            return

        if tag == "a" and "class" in attrs and "a-link-normal" in attrs["class"]:
            href = attrs.get("href", "")
            if "/dp/" in href:
                self.current["link"] = href

        if tag == "span":
            cls = attrs.get("class", "")
            if "a-size-medium" in cls:
                self.capture_title = True
            if "a-price-whole" in cls:
                self.capture_price = True
            if "a-offscreen" in cls and not self.current["price"]:
                self.capture_price = True
            if "a-icon-alt" in cls:
                self.capture_rating = True

        if tag == "span" and attrs.get("class") == "a-price a-text-price":
            self.capture_original = True

    def handle_data(self, data):
        if not self.current:
            return

        if self.capture_title:
            self.current["name"] += data.strip()

        if self.capture_price:
            self.current["price"] += data.strip()

        if self.capture_original:
            self.current["original_price"] += data.strip()

        if self.capture_rating:
            self.current["rating"] += data.strip()

    def handle_endtag(self, tag):
        if tag == "span":
            self.capture_title = False
            self.capture_price = False
            self.capture_original = False
            self.capture_rating = False

        if tag == "div" and self.current:
            if self.current.get("link"):
                self.products.append(self.current)
            self.current = {}


def fetch(url):
    r = requests.get(url, headers=HEADERS)
    return r.text if r.status_code == 200 else ""


def extract_products(html, base_url):
    parser = AmazonParser()
    parser.feed(html)

    results = []
    for p in parser.products:
        link = urljoin(base_url, p["link"])
        pid = p["id"] if p["id"] else extract_id(link)

        price = clean_price(p["price"])
        original = clean_price(p["original_price"])
        discount = calculate_discount(price, original)

        results.append({
            "id": pid,
            "name": p["name"],
            "link": link,
            "price": price,
            "original_price": original,
            "discount": discount,
            "rating": extract_rating(p["rating"])
        })
    return results


def extract_id(link):
    m = re.search(r"/dp/([A-Z0-9]+)", link)
    return m.group(1) if m else ""


def clean_price(text):
    text = re.sub(r"[^\d.]", "", text)
    return float(text) if text else ""


def extract_rating(text):
    m = re.search(r"([\d.]+)", text)
    return float(m.group(1)) if m else ""


def calculate_discount(price, original):
    if price and original and original > 0:
        return round((original - price) * 100 / original, 2)
    return ""


def get_next_page(html, base_url):
    class NextParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.next_link = None

        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == "a" and "class" in attrs and "s-pagination-next" in attrs["class"]:
                self.next_link = attrs.get("href")

    parser = NextParser()
    parser.feed(html)
    return urljoin(base_url, parser.next_link) if parser.next_link else None


def crawl(category_url):
    current_url = category_url
    all_products = []

    while current_url:
        html = fetch(current_url)
        if not html:
            break

        products = extract_products(html, current_url)
        all_products.extend(products)

        current_url = get_next_page(html, current_url)

    return all_products


def read_input_csv(path):
    urls = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            urls.append(row["url"])
    return urls


def write_output_csv(path, data):
    fields = ["id", "name", "link", "price", "original_price", "discount", "rating"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    input_file = "input.csv"
    output_file = "output.csv"

    urls = read_input_csv(input_file)

    final_data = []
    for url in urls:
        final_data.extend(crawl(url))

    write_output_csv(output_file, final_data)
