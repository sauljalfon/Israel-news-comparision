from datetime import timedelta
from airflow.sdk import DAG
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.timetables.trigger import CronTriggerTimetable
from pendulum import timezone

ACI_IP = "10.0.2.135"
RESOURCE_GROUP = "rg-israel-news-comparision-dev"
CONTAINER_GROUP = "aci-israel-news-comparision-dev"

default_args = {
    "owner": "sauljalfon",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="israel_news_pipeline",
    default_args=default_args,
    description="Daily Israel news intelligence pipeline",
    schedule=CronTriggerTimetable("@daily", timezone="Asia/Jerusalem"),
) as dag:

    start = EmptyOperator(task_id="start")

    extract_news = HttpOperator(
        task_id="extract_news",
        http_conn_id="aci_extractor_news",
        endpoint="/extract",
        method="POST",
        headers={"Content-Type": "application/json"},
        data='{"raw_path": "{{ ds }}/articles.ndjson"}',
        response_check=lambda response: response.status_code == 200,
    )

    extract_market = HttpOperator(
        task_id="extract_market",
        http_conn_id="aci_extractor_market",
        endpoint="/extract",
        method="POST",
        headers={"Content-Type": "application/json"},
        data='{"raw_path": "{{ ds }}/tase.ndjson", "date": "{{ ds }}"}',
        response_check=lambda response: response.status_code == 200,
    )

    enrich = HttpOperator(
        task_id="enrich",
        http_conn_id="aci_enrich",
        endpoint="/enrich",
        method="POST",
        headers={"Content-Type": "application/json"},
        data='{"raw_path": "{{ ds }}/articles.ndjson", "enriched_path": "{{ ds }}/articles.parquet"}',
        response_check=lambda response: response.status_code == 200,
    )

    transform = HttpOperator(
        task_id="transform",
        http_conn_id="aci_transform",
        endpoint="/transform",
        method="POST",
        headers={"Content-Type": "application/json"},
        data='{"enriched_path": "{{ ds }}/articles.parquet", "tase_path": "{{ ds }}/tase.ndjson", "processed_path": "{{ ds }}/articles.parquet"}',
        response_check=lambda response: response.status_code == 200,
    )

    synthesis = HttpOperator(
        task_id="synthesis",
        http_conn_id="aci_synthesis",
        endpoint="/synthesize",
        method="POST",
        headers={"Content-Type": "application/json"},
        data='{"processed_path": "{{ ds }}/articles.parquet", "report_path": "{{ ds }}/report.json"}',
        response_check=lambda response: response.status_code == 200,
    )

    start >> [extract_news, extract_market]
    extract_news >> enrich
    [enrich, extract_market] >> transform
    transform >> synthesis
