from pydantic import BaseModel


class ExtractRequest(BaseModel):
    raw_path: str


class ExtractResponse(BaseModel):
    raw_path: str
    total_articles: int
