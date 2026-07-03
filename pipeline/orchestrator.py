import os
import sys
import logging
from datetime import datetime, timezone
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.db.session import SessionLocal
from app.db.models.pipeline_run import PipelineRun

# Import components
from collectors.playwright_collector import collect_trustpilot_reviews
from collectors.reddit_collector import collect_reddit_reviews
from collectors.google_news_collector import collect_google_news
from collectors.playstore_collector import collect_playstore_reviews
from collectors.google_store_collector import collect_google_store_reviews

from nlp.cleaner import process_raw_mentions
from nlp.sentiment import run_sentiment_pipeline
from nlp.absa import run_absa_pipeline
from nlp.topic_modeling import run_topic_modeling_pipeline
from indexer.indexer import index_all_data

from alert_engine import check_all_alerts
from analytics.insight_generator import generate_insights_for_all_brands

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrator")

def run_stage(stage_name, func, *args, **kwargs):
    db = SessionLocal()
    run_log = PipelineRun(stage_name=stage_name, status="pending", started_at=datetime.now(timezone.utc))
    db.add(run_log)
    db.commit()
    db.refresh(run_log)
    
    try:
        logger.info(f"--- Starting Stage: {stage_name} ---")
        func(*args, **kwargs)
        run_log.status = "success"
        logger.info(f"--- Finished Stage: {stage_name} ---")
    except Exception as e:
        logger.error(f"Error in {stage_name}: {e}")
        run_log.status = "failed"
        run_log.error_message = traceback.format_exc()
        raise e
    finally:
        run_log.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.close()

def collect_all():
    try:
        collect_trustpilot_reviews()
    except Exception as e:
        logger.error(f"Trustpilot collection failed: {e}")
    try:
        collect_reddit_reviews(50)
    except Exception as e:
        logger.error(f"Reddit collection failed: {e}")
    try:
        collect_google_news(30)
    except Exception as e:
        logger.error(f"Google News collection failed: {e}")
    try:
        collect_playstore_reviews(100)
    except Exception as e:
        logger.error(f"Playstore collection failed: {e}")
    try:
        collect_google_store_reviews()
    except Exception as e:
        logger.error(f"Google Store collection failed: {e}")

def run_all():
    logger.info("=== Starting Unified Orchestrated Pipeline ===")
    
    stages = [
        ("collect", collect_all),
        ("clean", process_raw_mentions),
        ("sentiment", lambda: run_sentiment_pipeline(16)),
        ("absa", run_absa_pipeline),
        ("topics", run_topic_modeling_pipeline),
        ("index", index_all_data),
        ("alerts", check_all_alerts),
        ("insights", generate_insights_for_all_brands),
    ]
    
    for stage_name, func in stages:
        try:
            run_stage(stage_name, func)
        except Exception:
            logger.error(f"Pipeline failed at stage: {stage_name}. Halting execution of remaining stages.")
            break

    logger.info("=== Pipeline Execution Complete ===")

if __name__ == "__main__":
    run_all()
