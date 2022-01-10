import requests
import re
from urllib.parse import quote_plus, urljoin
from html.parser import HTMLParser

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

class SearchParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self.current = None
        self.capture_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "div" and attrs.get("data-component-type") == "s-search-result":
            self.current = {
                "id": attrs.get("data-asin"),
                "name": "",
                "link": ""
            }

        if not self.current:
            return

        if tag == "a" and "class" in attrs and "a-link-normal" in attrs["class"]:
            href = attrs.get("href", "")
            if "/dp/" in href:
                self.current["link"] = href

        if tag == "span" and "class" in attrs and "a-size-medium" in attrs["class"]:
            self.capture_title = True

    def handle_data(self, data):
        if self.capture_title and self.current:
            self.current["name"] += data.strip()

    def handle_endtag(self, tag):
        if tag == "span":
            self.capture_title = False

        if tag == "div" and self.current:
            if self.current.get("link"):
                self.results.append(self.current)
            self.current = None


def fetch(url):
    r = requests.get(url, headers=HEADERS)
    return r.text if r.status_code == 200 else ""


def extract_products(html, base_url):
    parser = SearchParser()
    parser.feed(html)

    results = []
    for r in parser.results:
        link = urljoin(base_url, r["link"])
        results.append({
            "id": r["id"],
            "name": r["name"],
            "link": link
        })
    return results


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


def search_amazon(query, max_pages=3):
    base = "https://www.amazon.in"
    url = f"{base}/s?k={quote_plus(query)}"

    rank = 1
    results = []

    current_url = url
    page = 1

    while current_url and page <= max_pages:
        html = fetch(current_url)
        if not html:
            break

        products = extract_products(html, base)

        for p in products:
            p["rank"] = rank
            results.append(p)
            rank += 1

        current_url = get_next_page(html, base)
        page += 1

    return results


if __name__ == "__main__":
    query = "laptops"

    results = search_amazon(query, max_pages=5)

    for r in results:
        print(f"{r['rank']}. {r['name']} ({r['id']})")
        print(r["link"])
        print("-" * 80)
