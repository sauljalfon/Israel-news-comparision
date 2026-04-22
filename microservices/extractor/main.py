from fastapi import FastAPI
from azure.storage.blob import BlobServiceClient

import feedparser
import requests
import trafilatura
import json
import logging

from models import ExtractRequest, ExtractResponse

app = FastAPI()
logger = logging.getLogger(__name__)


@app.get("/")
def root():
    return {"message": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractResponse)
def extract(req: ExtractRequest) -> ExtractResponse:
    all_articles = []
    blob_path = f"raw/{req.run_date}/articles.ndjson"
    for feed in RSS_FEEDS:
        articles = fetch_rss(feed)
        for article in articles:
            article["full_text"] = fetch_full_text(article["url"])
            all_articles.append(article)
    upload_to_blob(req.storage_connection_string, all_articles, blob_path)

    return ExtractResponse(
        run_date=req.run_date,
        total_articles=len(all_articles),
        blob_path=blob_path,
    )


RSS_FEEDS = [
    {"source": "toi", "language": "en", "url": "https://www.timesofisrael.com/feed/"},
    {
        "source": "jpost",
        "language": "en",
        "url": "https://www.jpost.com/rss/rssfeedsheadlines.aspx",
    },
]


def fetch_rss(feed: dict) -> list:
    try:
        parsed = feedparser.parse(feed["url"])
    except Exception as e:
        logger.warning(f"fetch_rss: failed for {feed['source']}: {e}")
        return []

    articles = []
    for entry in parsed.entries:
        articles.append(
            {
                "source": feed["source"],
                "language": feed["language"],
                "title": entry.title,
                "url": entry.link,
                "published": entry.published,
            }
        )
    return articles


def fetch_full_text(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, timeout=15, headers=headers)
        return trafilatura.extract(response.text) or ""

    except Exception as e:
        logger.warning(f"fetch_full_text: failed for {url}: {e}")
        return ""


def upload_to_blob(connection_string: str, articles: list, blob_path: str) -> None:
    client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = client.get_blob_client(container="raw", blob=blob_path)
    ndjson = "\n".join(json.dumps(article, ensure_ascii=False) for article in articles)
    blob_client.upload_blob(ndjson.encode("utf-8"), overwrite=True)
