from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Import our pipeline functions
import sys
import os
sys.path.append("/opt/airflow/pipeline")
sys.path.append("/opt/airflow/backend")

from orchestrator import collect_all
from nlp.cleaner import process_raw_mentions
from nlp.sentiment import run_sentiment_pipeline
from nlp.absa import run_absa_pipeline
from nlp.topic_modeling import run_topic_modeling_pipeline
from indexer.indexer import index_all_data
from alert_engine import check_all_alerts
from analytics.insight_generator import generate_insights_for_all_brands
from reports.report_generator import generate_weekly_report

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "social_product_intelligence_pipeline",
    default_args=default_args,
    description="Orchestrates ingestion, NLP cleanup, modeling, and dashboard indexing",
    schedule_interval=timedelta(hours=6),
    start_date=datetime(2026, 6, 15),
    catchup=False,
) as dag:

    task_collect = PythonOperator(
        task_id="collect_data",
        python_callable=collect_all
    )

    task_clean = PythonOperator(
        task_id="clean_and_deduplicate",
        python_callable=process_raw_mentions
    )

    task_sentiment = PythonOperator(
        task_id="sentiment_analysis",
        python_callable=lambda: run_sentiment_pipeline(batch_size=16)
    )

    task_absa = PythonOperator(
        task_id="aspect_based_sentiment",
        python_callable=run_absa_pipeline
    )

    task_topics = PythonOperator(
        task_id="topic_modeling",
        python_callable=run_topic_modeling_pipeline
    )

    task_index = PythonOperator(
        task_id="elasticsearch_indexing",
        python_callable=index_all_data
    )

    task_alerts = PythonOperator(
        task_id="run_alert_checks",
        python_callable=check_all_alerts
    )

    task_insights = PythonOperator(
        task_id="generate_insights",
        python_callable=generate_insights_for_all_brands
    )

    task_weekly_report = PythonOperator(
        task_id="generate_weekly_pdf_report",
        python_callable=generate_weekly_report
    )

    # DAG Dependency flow
    task_collect >> task_clean >> task_sentiment >> task_absa >> task_topics >> task_index >> task_alerts >> task_insights >> task_weekly_report
