from pydantic import BaseModel, Field


class CategoryCount(BaseModel):
    category: str
    count: int


class SituationReport(BaseModel):
    top_events: list[str] = Field(
        description="Top 3-5 events of the day, each as concise 1-2 sentences summary"
    )
    sentiment_summary: str = Field(
        description="Overall tone of today's news, mostly positive, negative, or mixed. Brief Explanation"
    )
    category_breakdown: list[CategoryCount] = Field(
        description="Count of articles per category, e.g. {'Security': 12, 'Politics': 8}"
    )
    market_correlation: str = Field(
        description="Brief analysis of how market movement relates to today's news sentiment"
    )
    cross_outlet_divergence: str = Field(
        description="Are Hebrew and English outlets telling the same story? Key differences if any."
    )
    headline_summary: str = Field(
        description="3-4 paragraph markdown summary of the day's news, suitable for a dashboard"
    )


class SynthesisRequest(BaseModel):
    processed_path: str
    report_path: str


class SynthesisResponse(BaseModel):
    report_path: str
    articles_analyzed: int
    top_event_count: int
