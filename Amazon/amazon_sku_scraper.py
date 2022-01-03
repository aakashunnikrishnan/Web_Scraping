import requests
from urllib.parse import urljoin
from html.parser import HTMLParser

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

class AmazonParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_product = False
        self.products = []
        self.current_link = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div" and "data-component-type" in attrs and attrs["data-component-type"] == "s-search-result":
            self.in_product = True
        if self.in_product and tag == "a" and "class" in attrs and "a-link-normal" in attrs["class"]:
            href = attrs.get("href")
            if href and "/dp/" in href:
                self.current_link = href

    def handle_endtag(self, tag):
        if tag == "div" and self.in_product:
            if self.current_link:
                self.products.append(self.current_link)
            self.in_product = False
            self.current_link = None


def fetch(url):
    r = requests.get(url, headers=HEADERS)
    return r.text if r.status_code == 200 else ""


def extract_products(html, base_url):
    parser = AmazonParser()
    parser.feed(html)
    return [urljoin(base_url, p) for p in parser.products]


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

        next_page = get_next_page(html, current_url)
        current_url = next_page

    return all_products


if __name__ == "__main__":
    url = "https://www.amazon.in/s?k=laptops"
    products = crawl(url)
    for p in products:
        print(p)
