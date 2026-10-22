
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

# LAB07: ニュースカテゴリーと検索ワード
TOPICS = {
    "海上保安庁": (
        "海上保安庁 OR 海保 OR 海上保安部 "
        "OR 海上保安署 OR 海上保安官 "
        "OR 海上保安学校 OR 海上保安大学校 "
        "OR 巡視船 OR 巡視艇"
    ),
    "尖閣諸島": "尖閣諸島",
}

# カテゴリーごとの最大記事数
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

    with urllib.request.urlopen(
        request, timeout=20
    ) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    articles = []
    seen = set()

    for item in root.findall("./channel/item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()

        if not title or not link:
            continue

        # 同じカテゴリー内の重複を除外
        if title in seen:
            continue

        seen.add(title)

        source = item.find("source")

        articles.append({
            "title": title,
            "link": link,
            "date": item.findtext("pubDate", ""),
            "source": (
                source.text
                if source is not None and source.text
                else ""
            )
        })

        if len(articles) >= MAX_ARTICLES:
            break

    return articles


def main():
    result = {
        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "topics": {}
    }

    for topic, keyword in TOPICS.items():
        print(f"Fetching: {topic}")

        articles = fetch_news(keyword)
        result["topics"][topic] = articles

        print(
            f"  {topic}: {len(articles)} articles"
        )

    output = Path(__file__).parent / "news.json"

    output.write_text(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("News fetched successfully!")
    print(f"Saved to: {output}")


if __name__ == "__main__":
    main()
