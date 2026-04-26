from pydantic import BaseModel


class TaseRequest(BaseModel):
    raw_path: str
    date: str


class TaseResponse(BaseModel):
    raw_path: str
    indices_fetched: int
