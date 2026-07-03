import sys
import os
import logging
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import numpy as np

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("sentiment")

# Add backend to path to import DB connection and models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from app.db.session import SessionLocal
from app.db.models.mention import ProcessedMention

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"

class SentimentAnalyzer:
    def __init__(self):
        logger.info(f"Loading tokenizer and model: {MODEL_NAME}...")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        # Select device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        logger.info(f"Tokenizer and model loaded on device: {self.device}")
        
        # RoBERTa mapping: 0 -> negative, 1 -> neutral, 2 -> positive
        self.labels_map = {
            0: "negative",
            1: "neutral",
            2: "positive"
        }

    def analyze_batch(self, texts: list[str]) -> list[dict]:
        if not texts:
            return []
            
        # Tokenize batch
        inputs = self.tokenizer(texts, padding=True, truncation=True, max_length=512, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        # Convert raw logits to probabilities via softmax
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1).cpu().numpy()
        
        results = []
        for prob in probs:
            idx = np.argmax(prob)
            results.append({
                "label": self.labels_map[idx],
                "score": float(prob[idx])
            })
        return results

def run_sentiment_pipeline(batch_size: int = 16):
    db = SessionLocal()
    try:
        # Fetch processed mentions that lack sentiment labels
        unlabeled = db.query(ProcessedMention).filter(
            ProcessedMention.sentiment_label == None
        ).all()
        
        if not unlabeled:
            logger.info("No unlabeled processed mentions found.")
            return
            
        logger.info(f"Found {len(unlabeled)} processed mentions requiring sentiment analysis.")
        
        # Load the analyzer model
        analyzer = SentimentAnalyzer()
        
        # Process in batches
        for i in range(0, len(unlabeled), batch_size):
            batch = unlabeled[i:i + batch_size]
            texts = [m.cleaned_text for m in batch]
            
            logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} items)...")
            results = analyzer.analyze_batch(texts)
            
            # Map labels and scores back to database objects
            for idx, res in enumerate(results):
                batch[idx].sentiment_label = res["label"]
                batch[idx].sentiment_score = res["score"]
                
            db.commit()
            logger.info(f"Batch {i//batch_size + 1} completed and saved.")
            
        logger.info("Sentiment pipeline execution finished successfully.")
        
    except Exception as e:
        logger.error(f"Error running sentiment pipeline: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_sentiment_pipeline(16)
