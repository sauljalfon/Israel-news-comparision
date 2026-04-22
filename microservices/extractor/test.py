from main import fetch_rss, RSS_FEEDS, fetch_full_text

israel = RSS_FEEDS[0]
output = fetch_rss(israel)

for article in output[:3]:
    text = fetch_full_text(article["url"])
    article["full_text"] = text
    print(article["title"])
    print(text)
    print("---")
