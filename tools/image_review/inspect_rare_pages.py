import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

urls = [
    "https://fohs.in/activities/poonjeri",
    "https://bishnoivillagesafarijodhpur.com/traditional-pottery-village-jodhpur-art-tour/",
    "https://ramaarya.blog/2022/03/14/rajasthan-jodhpur-navchokiya/",
]
for url in urls:
    print("URL", url)
    soup = BeautifulSoup(requests.get(url, timeout=30).text, "html.parser")
    for node in soup.select('meta[property="og:image"]'):
        print("OG", urljoin(url, node.get("content", "")))
    for node in soup.select("img"):
        src = node.get("src") or node.get("data-src") or node.get("data-lazy-src")
        if src:
            print("IMG", urljoin(url, src), node.get("alt", ""))
