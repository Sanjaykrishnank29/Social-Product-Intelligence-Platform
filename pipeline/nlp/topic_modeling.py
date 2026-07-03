import sys
import os
import logging
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from bertopic import BERTopic

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("topic_modeling")

# Add backend and pipeline to path to import DB models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.db.models.mention import ProcessedMention, TopicResult

def generate_topic_name(words: list[str]) -> str:
    # Helper to check if any of the keywords are in the topic's top words
    def has_any(keywords, top_words):
        return any(k in top_words for k in keywords)

    top_words_lower = [w.lower() for w in words]
    
    if has_any(["refund", "money", "charge", "payment", "pay", "deducted", "transaction", "amount"], top_words_lower):
        return "Refund & Payment Issues"
    elif has_any(["delivery", "late", "delay", "rider", "time", "speed", "arrive", "location", "order", "shipping", "courier", "package", "packaging"], top_words_lower):
        return "Delivery & Packaging Issues"
    elif has_any(["quality", "material", "fake", "original", "genuine", "damaged", "defective", "broken", "duplicate", "size", "fit", "fabric", "stitching"], top_words_lower):
        return "Product Quality & Defects"
    elif has_any(["price", "expensive", "cheap", "cost", "discount", "coupon", "deal", "offer", "value", "worth", "supercoin", "points"], top_words_lower):
        return "Price & Value Comparison"
    elif has_any(["return", "exchange", "replacement", "replaced", "cancel", "money back"], top_words_lower):
        return "Return & Refund Issues"
    elif has_any(["bug", "crash", "app", "ui", "ux", "update", "loading", "error", "open", "slow", "worst", "login", "checkout"], top_words_lower):
        return "App UX & Technical Errors"
    elif has_any(["support", "help", "care", "agent", "chat", "customer", "contact", "respond", "number"], top_words_lower):
        return "Customer Support & Service"
    
    # Fallback: join top 3 words capitalized
    return " / ".join(words[:3]).title()

def run_topic_modeling_pipeline():
    db = SessionLocal()
    try:
        # 1. Fetch all processed mentions
        mentions = db.query(ProcessedMention).all()
        if not mentions:
            logger.info("No processed mentions found in database. Exiting.")
            return

        logger.info(f"Retrieved {len(mentions)} processed mentions for topic modeling.")
        
        # Extract documents and associated mapping data
        docs = [m.cleaned_text for m in mentions]
        
        # 2. Configure BERTopic models for small dataset
        logger.info("Configuring UMAP and HDBSCAN models for small corpus size...")
        
        # UMAP for dimensionality reduction
        umap_model = UMAP(
            n_neighbors=5,
            n_components=5,
            min_dist=0.0,
            metric="cosine",
            random_state=42
        )
        
        # HDBSCAN for clustering
        hdbscan_model = HDBSCAN(
            min_cluster_size=3,
            min_samples=2,
            metric="euclidean",
            cluster_selection_method="eom",
            prediction_data=True
        )
        
        # SentenceTransformer for embedding generation
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Build BERTopic pipeline
        topic_model = BERTopic(
            embedding_model=embedding_model,
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            verbose=True
        )
        
        # 3. Fit model
        logger.info("Generating embeddings and fitting BERTopic model...")
        topics, probs = topic_model.fit_transform(docs)
        
        # 4. Outlier reduction
        # Map outliers (topic -1) to their closest semantic cluster based on embeddings
        logger.info("Performing outlier reduction to assign general reviews to closest themes...")
        try:
            new_topics = topic_model.reduce_outliers(docs, topics, strategy="embeddings")
            topics = new_topics
        except Exception as e:
            logger.warning(f"Outlier reduction failed (skipping): {e}")

        # 5. Get topic naming mapping
        topic_names = {}
        for topic_id in set(topics):
            if topic_id == -1:
                topic_names[topic_id] = "General Feedback"
            else:
                words = [word for word, _ in topic_model.get_topic(topic_id)[:5]]
                topic_names[topic_id] = generate_topic_name(words)
                logger.info(f"Discovered Topic {topic_id} -> '{topic_names[topic_id]}' (Keywords: {words})")

        # 6. Save results to DB (Clear old topic results first as topics are globally clustered)
        logger.info("Clearing old topic results and saving new mappings to DB...")
        db.query(TopicResult).delete()
        
        results_count = 0
        for mention, topic_id in zip(mentions, topics):
            topic_name = topic_names.get(topic_id, "General Feedback")
            
            topic_res = TopicResult(
                source_id=mention.id,
                brand=mention.brand,
                topic_id=int(topic_id),
                topic_name=topic_name
            )
            db.add(topic_res)
            results_count += 1
            
        db.commit()
        logger.info(f"Successfully processed and stored {results_count} topic mappings.")

    except Exception as e:
        logger.error(f"Error running topic modeling pipeline: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_topic_modeling_pipeline()
