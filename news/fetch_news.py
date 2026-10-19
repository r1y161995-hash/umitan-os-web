import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

# ニュースの検索テーマ
TOPICS = {
    "海上保安庁": "海上保安庁",
}

# テーマごとの最大取得件数
MAX_ARTICLES = 10


def fetch_news(keyword):
    query = urllib.parse.quote(keyword)
    url = (
        f"https://news.google.com/rss/search?q={query}"
        "&hl=ja&gl=JP&ceid=JP:ja"
    )

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    articles = []

    for item in root.findall("./channel/item")[:MAX_ARTICLES]:
        source = item.find("source")

        articles.append({
            "title": item.findtext("title", ""),
            "link": item.findtext("link", ""),
            "date": item.findtext("pubDate", ""),
            "source": source.text if source is not None else ""
        })

    return articles


def main():
    result = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "topics": {}
    }

    for topic, keyword in TOPICS.items():
        result["topics"][topic] = fetch_news(keyword)

    output = Path(__file__).parent / "news.json"
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("News fetched successfully!")
    print(f"Saved to: {output}")


if __name__ == "__main__":
    main()
