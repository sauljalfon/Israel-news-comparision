from fastapi import FastAPI
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

import pandas as pd
import json
import logging
import os
import io

from models import TransformRequest, TransformResponse

load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
blob_client = BlobServiceClient.from_connection_string(
    str(AZURE_STORAGE_CONNECTION_STRING)
)

app = FastAPI()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/transform", response_model=TransformResponse)
def transform(req: TransformRequest) -> TransformResponse:
    articles = read_enriched(req.enriched_path)
    tase_records = read_tase(req.tase_path)

    tase_pivot = pivot_tase(tase_records)

    for key, value in tase_pivot.items():
        articles[key] = value

    write_processed(articles, req.processed_path)

    return TransformResponse(
        processed_path=req.processed_path,
        total_rows=len(articles),
        tase_indices=len(tase_pivot),
    )


def read_enriched(enriched_path: str) -> pd.DataFrame:
    logger.info(f"Reading enriched data from {enriched_path}")
    container = blob_client.get_container_client("enriched")
    blob = container.get_blob_client(enriched_path).download_blob().readall()
    df = pd.read_parquet(io.BytesIO(blob))
    logger.info(f"Read {len(df)} rows from {enriched_path}")
    return df


def read_tase(tase_path: str) -> list[dict]:
    logger.info(f"Reading tase data from {tase_path}")
    container = blob_client.get_container_client("raw")
    data = container.get_blob_client(tase_path).download_blob().readall()
    records = []
    for line in data.decode("utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    logger.info(f"Read {len(records)} records from {tase_path}")
    return records


def pivot_tase(tase_records: list[dict]) -> dict:
    pivot = {}
    for record in tase_records:
        name = record["index_name"].lower().replace("-", "")
        for field in ["open", "close", "high", "low", "volume"]:
            pivot[f"{name}_{field}"] = record[field]
    return pivot


def write_processed(df: pd.DataFrame, processed_path: str):
    logger.info(f"Writing processed data to {processed_path}")
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)
    container = blob_client.get_container_client("processed")
    blob = container.get_blob_client(processed_path)
    blob.upload_blob(buffer, overwrite=True)
    logger.info(f"Wrote {len(df)} rows to {processed_path}")
