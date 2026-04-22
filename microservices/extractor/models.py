from pydantic import BaseModel


class ExtractRequest(BaseModel):
    run_date: str
    storage_connection_string: str


class ExtractResponse(BaseModel):
    run_date: str
    total_articles: int
    blob_path: str
