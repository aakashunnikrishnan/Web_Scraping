import requests
from html.parser import HTMLParser
from urllib.parse import quote_plus

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


class QuoraParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.capture = False
        self.titles = []
        self.current = ""

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "a":
            href = attrs.get("href", "")
            if "/profile/" not in href and "/answer/" not in href:
                cls = attrs.get("class", "")
                if "q-box" in cls:
                    self.capture = True

    def handle_data(self, data):
        if self.capture:
            self.current += data.strip()

    def handle_endtag(self, tag):
        if tag == "a" and self.capture:
            if self.current:
                self.titles.append(self.current)
            self.capture = False
            self.current = ""


def fetch(url):
    r = requests.get(url, headers=HEADERS)
    return r.text if r.status_code == 200 else ""


def extract_questions(html):
    parser = QuoraParser()
    parser.feed(html)
    return list(set(parser.titles))


def search_quora(query):
    url = f"https://www.quora.com/search?q={quote_plus(query)}"
    html = fetch(url)
    return extract_questions(html)


if __name__ == "__main__":
    query = "data engineering"

    questions = search_quora(query)

    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")
