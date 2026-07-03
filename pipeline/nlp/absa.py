import sys
import os
import json
import re
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("absa")

# Add backend and pipeline to path to import DB models and SentimentAnalyzer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.db.models.mention import ProcessedMention, AspectResult
from nlp.sentiment import SentimentAnalyzer

# Load aspect keywords definition
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../config/aspects.json'))

def load_aspects_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def split_clauses(text: str) -> list[str]:
    # Split sentences by common punctuation and contrastive conjunctions
    clauses = re.split(r'[,.;]|\bbut\b|\bhowever\b|\balthough\b|\band\b', text)
    return [c.strip() for c in clauses if c.strip()]

def run_absa_pipeline():
    db = SessionLocal()
    try:
        aspects_config = load_aspects_config()
        
        # Get all processed reviews that don't have aspect results yet
        unprocessed = db.query(ProcessedMention).outerjoin(
            AspectResult, ProcessedMention.id == AspectResult.source_id
        ).filter(AspectResult.id == None).all()
        
        if not unprocessed:
            logger.info("No new processed mentions to analyze for aspects.")
            return
            
        logger.info(f"Found {len(unprocessed)} processed mentions to run ABSA on.")
        
        # Load Sentiment Analyzer to score clauses
        analyzer = SentimentAnalyzer()
        
        results_count = 0
        for review in unprocessed:
            clauses = split_clauses(review.cleaned_text)
            
            # Detect which aspects are mentioned
            for aspect, keywords in aspects_config.items():
                pattern = r'\b(' + '|'.join(map(re.escape, keywords)) + r')\b'
                
                # Check if aspect matches
                if re.search(pattern, review.cleaned_text):
                    # Check which clauses contain this aspect
                    matched_clauses = [c for c in clauses if re.search(pattern, c)]
                    
                    sentiment_label = review.sentiment_label
                    sentiment_score = review.sentiment_score
                    
                    # If we isolated a clause, analyze it specifically for target sentiment
                    if matched_clauses:
                        # Grab the first matching clause
                        target_clause = matched_clauses[0]
                        # Only run inference if clause is significantly different from full text and not too short
                        if len(target_clause.split()) >= 3 and len(target_clause) < len(review.cleaned_text) * 0.8:
                            try:
                                res = analyzer.analyze_batch([target_clause])[0]
                                sentiment_label = res["label"]
                                sentiment_score = res["score"]
                                logger.info(f"Clause Sentiment (Aspect: {aspect}): '{target_clause}' -> {sentiment_label.upper()} ({sentiment_score:.2f})")
                            except Exception as e:
                                logger.error(f"Error classifying clause sentiment: {e}")
                                
                    # Store AspectResult
                    aspect_res = AspectResult(
                        source_id=review.id,
                        brand=review.brand,
                        aspect=aspect,
                        sentiment_label=sentiment_label,
                        sentiment_score=sentiment_score
                    )
                    db.add(aspect_res)
                    results_count += 1
                    
        db.commit()
        logger.info(f"Successfully processed aspects and saved {results_count} aspect results.")
        
    except Exception as e:
        logger.error(f"Error running ABSA pipeline: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_absa_pipeline()
