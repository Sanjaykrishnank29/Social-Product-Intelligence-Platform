import sys
import os
import logging
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("indexer")

# Add backend to path to import DB models and sessions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from app.db.session import SessionLocal
from app.db.models.mention import ProcessedMention, AspectResult, TopicResult

INDEX_NAME = "processed_mentions"

def get_es_client():
    es_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
    es_port = os.getenv("ELASTICSEARCH_PORT", "9200")
    es_url = f"http://{es_host}:{es_port}"
    logger.info(f"Connecting to Elasticsearch at: {es_url}")
    return Elasticsearch(es_url, request_timeout=30)

def create_index_mapping(es: Elasticsearch):
    mapping = {
        "mappings": {
            "properties": {
                "mention_id": { "type": "long" },
                "brand": { "type": "keyword" },
                "source": { "type": "keyword" },
                "author": { "type": "keyword" },
                "post_date": { "type": "date" },
                "cleaned_text": { "type": "text", "analyzer": "english" },
                "sentiment_label": { "type": "keyword" },
                "sentiment_score": { "type": "float" },
                "aspects": {
                    "type": "nested",
                    "properties": {
                        "aspect": { "type": "keyword" },
                        "sentiment_label": { "type": "keyword" },
                        "sentiment_score": { "type": "float" }
                    }
                },
                "topic_name": { "type": "keyword" }
            }
        }
    }
    
    if es.indices.exists(index=INDEX_NAME):
        logger.info(f"Deleting existing index: {INDEX_NAME}")
        es.indices.delete(index=INDEX_NAME)
        
    logger.info(f"Creating index: {INDEX_NAME} with custom nested mappings")
    es.indices.create(index=INDEX_NAME, body=mapping)

def index_all_data():
    db = SessionLocal()
    es = get_es_client()
    
    try:
        # 1. Initialize mappings
        create_index_mapping(es)
        
        # 2. Fetch all processed mentions
        logger.info("Fetching processed mentions from database...")
        mentions = db.query(ProcessedMention).all()
        if not mentions:
            logger.info("No processed mentions to index.")
            return
            
        logger.info(f"Retrieved {len(mentions)} processed mentions to prepare for indexing.")
        
        # Pre-fetch aspects and topics to optimize SQL joins
        logger.info("Grouping aspects and topics by source_id...")
        aspects_rows = db.query(AspectResult).all()
        topics_rows = db.query(TopicResult).all()
        
        aspects_by_mention = {}
        for a in aspects_rows:
            aspects_by_mention.setdefault(a.source_id, []).append({
                "aspect": a.aspect,
                "sentiment_label": a.sentiment_label,
                "sentiment_score": float(a.sentiment_score)
            })
            
        topics_by_mention = {t.source_id: t.topic_name for t in topics_rows}
        
        # 3. Format actions for bulk helper
        actions = []
        for mention in mentions:
            doc = {
                "_index": INDEX_NAME,
                "_id": str(mention.id),
                "mention_id": mention.id,
                "brand": mention.brand,
                "source": mention.source,
                "author": mention.author,
                "post_date": mention.post_date.isoformat() if mention.post_date else None,
                "cleaned_text": mention.cleaned_text,
                "sentiment_label": mention.sentiment_label,
                "sentiment_score": float(mention.sentiment_score) if mention.sentiment_score is not None else None,
                "aspects": aspects_by_mention.get(mention.id, []),
                "topic_name": topics_by_mention.get(mention.id, "General Feedback")
            }
            actions.append(doc)
            
        # 4. Perform bulk indexing
        logger.info(f"Executing bulk index payload of {len(actions)} documents...")
        success, failed = bulk(es, actions)
        logger.info(f"Indexing complete! Successfully indexed {success} documents. Failed: {len(failed) if isinstance(failed, list) else failed}")
        
    except Exception as e:
        logger.error(f"Error during Elasticsearch indexing: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    index_all_data()
