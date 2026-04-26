from fastapi import FastAPI
from numpy import average
from openai import OpenAI
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from pandas import pandas as pd
import io

import os
import logging
import json

from models import EnrichRequest, EnrichResponse, ArticleEnrichment

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
blob_client = BlobServiceClient.from_connection_string(
    str(AZURE_STORAGE_CONNECTION_STRING)
)

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/enrich", response_model=EnrichResponse)
def enrich(req: EnrichRequest) -> EnrichResponse:
    articles = read_raw(req.raw_path)

    enriched_articles = []
    enrichments = []
    failed = 0
    for article in articles:
        try:
            result = enrich_article(article)
            if result is None:
                raise ValueError("Parsed Result is None")
            enriched_articles.append(article)
            enrichments.append(result)
        except Exception as e:
            logger.warning(f"Failed to enrich article {article.get('title')}: {e}")
            failed += 1

    write_enriched(enriched_articles, enrichments, req.enriched_path)

    categories_found = list(set((e.category for e in enrichments)))
    average_sentiment = sum(float(e.sentiment) for e in enrichments) / len(enrichments)
    breaking_count = sum(1 for e in enrichments if e.category == "Breaking News")

    return EnrichResponse(
        enriched_path=req.enriched_path,
        articles_read=len(articles),
        articles_enriched=len(enrichments),
        articles_failed=failed,
        categories_found=categories_found,
        avg_sentiment=round(average_sentiment, 3),
        breaking_count=breaking_count,
    )


def read_raw(raw_path: str) -> list[dict]:
    logger.info(f"Reading raw articles from {raw_path}")
    container_client = blob_client.get_container_client("raw")
    blob = container_client.get_blob_client(raw_path)
    data = blob.download_blob().readall()
    articles = []
    for line in data.decode("utf-8").splitlines():
        line = line.strip()
        if line:
            articles.append(json.loads(line))
    logger.info(f"Read {len(articles)} articles")
    return articles


def enrich_article(article: dict) -> ArticleEnrichment | None:
    logger.info(f"Enriching article {article.get('title')}")
    prompt = f"""
    You are an expert in analyzing news articles. Analyze the following news article and return strucutured data.

    Title:  {article.get("title", '')}
    Source: {article.get("source"), ''}
    Language: {article.get("language"), ''}
    Full Text: {article.get("full_text"), ''}
    """

    response = openai_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a news analyst that returns strucutured JSON only.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format=ArticleEnrichment,
    )
    return response.choices[0].message.parsed


def write_enriched(
    articles: list[dict], enrichments: list[ArticleEnrichment], enrichment_path: str
) -> None:
    logger.info(f"Writing {len(enrichments)} enriched articles to {enrichment_path}")
    rows = []
    for article, enrichment in zip(articles, enrichments):
        row = {
            **article,
            "category": enrichment.category,
            "sentiment": float(enrichment.sentiment),
            "urgency": enrichment.urgency,
            "geographic_scope": enrichment.geographic_scope,
            "summary": enrichment.summary,
            "keywords": enrichment.keywords,
            "entities_people": json.dumps(enrichment.entities.people),
            "entities_orgs": json.dumps(enrichment.entities.organizations),
            "entities_places": json.dumps(enrichment.entities.places),
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)

    container_client = blob_client.get_container_client("enriched")
    blob = container_client.get_blob_client(enrichment_path)
    blob.upload_blob(buffer.read(), overwrite=True)
    logger.info(f"Uploaded {len(enrichments)} enriched articles to {enrichment_path}")
