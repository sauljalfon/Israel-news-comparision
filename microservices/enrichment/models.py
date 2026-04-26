from pydantic import BaseModel, Field
from typing import List, Optional


class ArticleEntities(BaseModel):
    people: List[str]
    places: List[str]
    organizations: List[str]


class ArticleEnrichment(BaseModel):
    category: str = Field(
        description="One of: Security, Politics, Economy, Tech, Society, Culture, Health, Other"
    )
    sentiment: str = Field(
        description="Sentiment Score: -1.0 (very negative) to 1.0 (very positive)"
    )
    urgency: str = Field(description="One of: Breaking, Developing, Background")
    geographic_scope: str = Field(description="One of: Local, Regional, International")
    summary: str = Field(description="2-3 sentences summary of the article")
    keywords: list[str] = Field(description="5 to 10 topic keywords")
    entities: ArticleEntities
    cross_lang_match_hint: Optional[str] = Field(
        default=None,
        description="If this article appears to cover the same event as other article in a different language, describe the topic briefly. Otherwise Null",
    )


class EnrichRequest(BaseModel):
    raw_path: str
    enriched_path: str


class EnrichResponse(BaseModel):
    enriched_path: str
    articles_read: int
    articles_enriched: int
    articles_failed: int
    categories_found: list[str]
    avg_sentiment: float
    breaking_count: int
