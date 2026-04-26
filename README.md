# Israel News Intelligence Pipeline

A daily automated pipeline that ingests Israeli news from multiple outlets (Hebrew + English)
alongside TASE stock market data, enriches articles via LLM, transforms through a medallion
architecture on Azure, and synthesizes a daily intelligence report.

## Architecture

```
Airflow (Docker on Azure VM) — orchestration
    │
    ├─► News Extractor (FastAPI)         → Bronze: raw/YYYY-MM-DD/articles.ndjson
    │     RSS feeds from Israeli outlets
    │
    ├─► TASE Extractor (FastAPI)         → Bronze: raw/YYYY-MM-DD/tase.ndjson
    │     TA-125 & TA-35 via yfinance
    │
    ├─► Enrichment Service (FastAPI)     → Silver: enriched/YYYY-MM-DD/articles.parquet
    │     OpenAI gpt-4o-mini structured outputs
    │     category, sentiment, urgency, entities, summary
    │
    ├─► Transform Service (FastAPI)      → Gold: processed/YYYY-MM-DD/articles.parquet
    │     Merges enriched articles with pivoted TASE data
    │
    └─► Synthesis Service (FastAPI)      → Reports: reports/YYYY-MM-DD/report.json
          Daily situation report: top events, sentiment,
          market correlation, cross-outlet divergence
```

## Medallion Architecture

| Layer   | Container    | Format  | Content                         |
| ------- | ------------ | ------- | ------------------------------- |
| Bronze  | `raw/`       | NDJSON  | Raw articles + raw TASE data    |
| Silver  | `enriched/`  | Parquet | LLM-enriched articles           |
| Gold    | `processed/` | Parquet | Articles + pivoted TASE columns |
| Reports | `reports/`   | JSON    | Daily situation reports         |

## Infrastructure

All infrastructure is provisioned via **Terraform** and runs on Azure:

- **Azure Container Registry** — stores Docker images for all microservices
- **Azure Container Instances** — runs microservices on a private VNet (no public exposure)
- **Azure Blob Storage** — medallion data lake (Bronze → Silver → Gold → Reports)
- **Azure Synapse** — serverless SQL queries over Gold Parquet via external tables
- **Azure VM (B2s)** — runs Airflow via Docker, orchestrates the pipeline
- **VNet** — private networking between VM and ACI; microservices are not publicly accessible

## Project Structure

```
israel-news-comparision/
├── airflow/
│   ├── dags/
│   │   └── news_dag.py            # Airflow DAG — daily orchestration
│   └── docker-compose.yaml        # Airflow Docker setup
├── microservices/
│   ├── extractor_news/            # News extraction from RSS feeds
│   ├── extractor_market/          # TASE market data extraction
│   ├── enrichment/                # LLM enrichment (OpenAI structured outputs)
│   ├── transform/                 # Silver + TASE → Gold merge
│   └── synthesis/                 # Daily situation report generation
├── synapse/
│   └── schema.sql                 # External table definition for Gold data
└── terraform/                     # All Azure infrastructure as code
```

## Microservice API Contracts

Each microservice is a FastAPI app running on its own port within a shared ACI container group.

| Service        | Port | Endpoint           | Input                                          | Output           |
| -------------- | ---- | ------------------ | ---------------------------------------------- | ---------------- |
| News Extractor | 8000 | `POST /extract`    | `raw_path`                                     | NDJSON → Bronze  |
| TASE Extractor | 8001 | `POST /extract`    | `raw_path`, `date`                             | NDJSON → Bronze  |
| Enrichment     | 8002 | `POST /enrich`     | `raw_path`, `enriched_path`                    | Parquet → Silver |
| Transform      | 8003 | `POST /transform`  | `enriched_path`, `tase_path`, `processed_path` | Parquet → Gold   |
| Synthesis      | 8004 | `POST /synthesize` | `processed_path`, `report_path`                | JSON → Reports   |

## LLM Enrichment

Each article is enriched using OpenAI `gpt-4o-mini` with structured outputs:

- **Category** — Security, Politics, Economy, Tech, Society, Culture, Health, Other
- **Sentiment** — float from -1.0 to 1.0
- **Urgency** — Breaking, Developing, Background
- **Geographic scope** — Local, Regional, International
- **Summary** — 2-3 sentence English summary
- **Keywords** — 5-10 topic keywords
- **Entities** — people, places, organizations
- **Cross-language match hint** — for Hebrew/English article matching

## Pipeline Flow

The Airflow DAG runs daily and executes tasks in this order:

1. **Extract news** and **extract TASE data** (parallel)
2. **Enrich** articles via LLM (depends on news extraction)
3. **Transform** — merge enriched articles with TASE data (depends on enrichment + TASE)
4. **Synthesize** — generate daily situation report (depends on transform)

## Tech Stack

- **Orchestration** — Apache Airflow 3.x
- **Microservices** — Python, FastAPI, Docker
- **LLM** — OpenAI gpt-4o-mini (structured outputs)
- **Storage** — Azure Blob Storage (ADLS Gen2)
- **Compute** — Azure Container Instances, Azure VM
- **Analytics** — Azure Synapse (serverless SQL)
- **IaC** — Terraform
- **Data formats** — NDJSON (Bronze), Parquet (Silver/Gold), JSON (Reports)

## Setup

### Prerequisites

- Azure subscription
- Terraform installed
- Docker installed
- OpenAI API key

### Deploy infrastructure

```bash
cd terraform
source .env  # TF_VAR_openai_api_key, TF_VAR_synapse_sql_admin_password
terraform init
terraform apply
```

### Build and push microservices

```bash
az acr login --name acrilnewscompdev

cd microservices/extractor_news && docker build -t extractor-news . && \
docker tag extractor-news acrilnewscompdev.azurecr.io/extractor-news:latest && \
docker push acrilnewscompdev.azurecr.io/extractor-news:latest

# Repeat for extractor_market, enrichment, transform, synthesis
```

### Run Airflow

```bash
cd airflow
echo "AIRFLOW_UID=$(id -u)" > .env
echo "AIRFLOW__CORE__LOAD_EXAMPLES=false" >> .env
echo "_PIP_ADDITIONAL_REQUIREMENTS=apache-airflow-providers-http" >> .env
docker compose up airflow-init
docker compose up -d
```

## News Sources

| Source          | Language |
| --------------- | -------- |
| Times of Israel | English  |
| Jerusalem Post  | English  |

_Additional Hebrew and English outlets planned._
