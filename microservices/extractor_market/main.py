from fastapi import FastAPI
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from datetime import datetime, timedelta

import yfinance as yf
import json
import logging as log
import os

from models import TaseRequest, TaseResponse

load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
blob_client = BlobServiceClient.from_connection_string(
    str(AZURE_STORAGE_CONNECTION_STRING)
)

app = FastAPI()
logger = log.getLogger(__name__)
log.basicConfig(level=log.INFO)

INDICES = [
    {"symbol": "^TA125.TA", "name": "TA-125"},
    {"symbol": "TA35.TA", "name": "TA-35"},
]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract", response_model=TaseResponse)
def extract(req: TaseRequest) -> TaseResponse:
    data = fetch_tase(req.date)
    upload_to_blob(data, req.raw_path)
    return TaseResponse(
        raw_path=req.raw_path,
        indices_fetched=len(data),
    )


def fetch_tase(date: str) -> list[dict]:
    logger.info(f"Fetching TASE for {date}")
    next_day = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )
    results = []
    for index in INDICES:
        ticker = yf.Ticker(index["symbol"])
        data = ticker.history(start=date, end=next_day)
        if data.empty:
            logger.warning(f"No data for {index['name']} on {date}")
            continue
        row = data.iloc[0]
        results.append(
            {
                "date": date,
                "index_name": index["name"],
                "symbol": index["symbol"],
                "open": float(row["Open"]),
                "close": float(row["Close"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "volume": int(row["Volume"]),
            }
        )
        logger.info(f"Fetched {index['name']} on {date}: close={row['Close']:.2f}")
    return results


def upload_to_blob(data: list[dict], raw_path: str) -> None:
    logger.info(f"Uploading {len(data)} records to {raw_path}")
    container_client = blob_client.get_container_client("raw")
    blob = container_client.get_blob_client(raw_path)
    ndjson = "\n".join(json.dumps(record) for record in data)
    blob.upload_blob(ndjson.encode("utf-8"), overwrite=True)
    logger.info(f"Uploaded {len(data)} records to {raw_path}")
