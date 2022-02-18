import requests

def get_trends():
    url = "https://trends24.in/india/"
    r = requests.get(url)

    import re
    trends = re.findall(r'<a[^>]*>(.*?)</a>', r.text)

    return list(set([t.strip() for t in trends if "#" in t]))


if __name__ == "__main__":
    trends = get_trends()

    for t in trends[:10]:
        print(t)
