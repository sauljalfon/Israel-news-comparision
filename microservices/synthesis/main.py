from fastapi import FastAPI
from openai import OpenAI
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

import pandas as pd
import json
import logging
import os
import io

from models import SynthesisRequest, SynthesisResponse, SituationReport

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
blob_client = BlobServiceClient.from_connection_string(
    str(AZURE_STORAGE_CONNECTION_STRING)
)

app = FastAPI()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/synthesize", response_model=SynthesisResponse)
def synthesize(req: SynthesisRequest) -> SynthesisResponse:
    df = read_processed(req.processed_path)
    report = generate_report(df)
    write_report(report, req.report_path)

    return SynthesisResponse(
        report_path=req.report_path,
        articles_analyzed=len(df),
        top_event_count=len(report.top_events),
    )


def read_processed(processed_path: str) -> pd.DataFrame:
    logger.info(f"Reading processed data from {processed_path}")
    container_client = blob_client.get_container_client("processed")
    blob = container_client.get_blob_client(processed_path)
    data = blob.download_blob().readall()
    df = pd.read_parquet(io.BytesIO(data))
    logger.info(f"Read {len(df)} rows from {processed_path}")
    return df


def generate_report(df: pd.DataFrame) -> SituationReport:
    article_summaries = []
    for _, row in df.iterrows():
        article_summaries.append(
            f"[{row['source']}|{row['language']}|{row['category']}|sentiment:{row['sentiment']}] {row['title']}: {row['summary']}"
        )

    first = df.iloc[0]
    market_lines = [
        f"TA-125: open={first.get('ta125_open')}, close={first.get('ta125_close')}, high={first.get('ta125_high')}, low={first.get('ta125_low')}",
        f"TA-35: open={first.get('ta35_open')}, close={first.get('ta35_close')}, high={first.get('ta35_high')}, low={first.get('ta35_low')}",
    ]

    prompt = f"""
    You are an intelligence analyst covering Israel. Analyze today's news and market data and produce a daily situation report.

    Today's articles ({len(df)} total):
        {chr(10).join(article_summaries)}

    Market lines:
        {chr(10).join(market_lines)}
    """

    logger.info(f"Sending {len(df)} articles to OpenAI for synthesis")

    response = openai_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an intelligence analyst that produces structured daily situation reports.",
            },
            {"role": "user", "content": prompt},
        ],
        response_format=SituationReport,
    )

    result = response.choices[0].message.parsed
    if result is None:
        raise Exception("No result from OpenAI")
    return result


def write_report(report: SituationReport, report_path: str) -> None:
    logger.info(f"Writing report to {report_path}")
    container_client = blob_client.get_container_client("reports")
    blob = container_client.get_blob_client(report_path)
    blob.upload_blob(report.model_dump_json().encode("utf-8"), overwrite=True)
    logger.info(f"Wrote report to {report_path}")
