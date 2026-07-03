import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("master_pipeline")

# Add paths to sys.path to allow absolute imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'pipeline')))

# Import Pipeline Components
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

def main():
    logger.info("=== Starting Master Pipeline Execution ===")
    
    # Phase 1: Ingest Data (Collectors)
    logger.info("\n--- Phase 1: Running Data Ingestion (Collectors) ---")
    
    logger.info("1. Running Playwright Trustpilot Collector...")
    try:
        collect_trustpilot_reviews()
    except Exception as e:
        logger.error(f"Trustpilot collector failed: {e}")
        
    logger.info("2. Running Reddit Collector...")
    try:
        collect_reddit_reviews(50)
    except Exception as e:
        logger.error(f"Reddit collector failed: {e}")
        
    logger.info("3. Running Google News Collector...")
    try:
        collect_google_news(30)
    except Exception as e:
        logger.error(f"Google News collector failed: {e}")
        
    logger.info("4. Running Playstore Collector...")
    try:
        collect_playstore_reviews(100)
    except Exception as e:
        logger.error(f"Playstore collector failed: {e}")
        
    logger.info("5. Running Google Store Collector...")
    try:
        collect_google_store_reviews()
    except Exception as e:
        logger.error(f"Google Store collector failed: {e}")
        
    # Phase 2: Data Cleaning
    logger.info("\n--- Phase 2: Running Data Cleaning & Validation ---")
    try:
        process_raw_mentions()
    except Exception as e:
        logger.error(f"Data cleaning failed: {e}")
        
    # Phase 3: Sentiment Classification
    logger.info("\n--- Phase 3: Running Sentiment Analysis (RoBERTa) ---")
    try:
        run_sentiment_pipeline(16)
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        
    # Phase 4: Aspect-Based Sentiment Analysis (ABSA)
    logger.info("\n--- Phase 4: Running Aspect-Based Sentiment Analysis (ABSA) ---")
    try:
        run_absa_pipeline()
    except Exception as e:
        logger.error(f"ABSA pipeline failed: {e}")
        
    # Phase 5: Topic Modeling
    logger.info("\n--- Phase 5: Running BERTopic Modeling ---")
    try:
        run_topic_modeling_pipeline()
    except Exception as e:
        logger.error(f"Topic modeling failed: {e}")
        
    # Phase 6: Elasticsearch Indexing
    logger.info("\n--- Phase 6: Indexing Data to Elasticsearch ---")
    try:
        index_all_data()
    except Exception as e:
        logger.error(f"Elasticsearch indexing failed: {e}")
        
    logger.info("\n=== Master Pipeline Execution Completed! ===")

if __name__ == "__main__":
    main()
