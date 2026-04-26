from pydantic import BaseModel


class TransformRequest(BaseModel):
    enriched_path: str
    tase_path: str
    processed_path: str


class TransformResponse(BaseModel):
    processed_path: str
    total_rows: int
    tase_indices: int
