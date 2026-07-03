import sys
import os
import re
import logging
import emoji
from langdetect import detect

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("cleaner")

# Add backend to path to import DB connection and models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from app.db.session import SessionLocal
from app.db.models.mention import RawMention, ProcessedMention

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Convert to lowercase
    text = text.lower()
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # Remove Emojis using emoji package
    text = emoji.replace_emoji(text, replace='')
    # Remove excess whitespace and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def detect_language(text: str) -> str:
    # Short reviews (less than 3 words) are hard for langdetect to identify accurately.
    # Classify them as 'en' defaults if short.
    if len(text.split()) < 3:
        return 'en'
    try:
        return detect(text)
    except Exception:
        return 'en'

def process_raw_mentions():
    db = SessionLocal()
    try:
        # Find raw mentions that have not been processed yet (matching on source_id)
        unprocessed = db.query(RawMention).outerjoin(
            ProcessedMention, RawMention.id == ProcessedMention.source_id
        ).filter(ProcessedMention.id == None).all()
        
        if not unprocessed:
            logger.info("No new raw mentions to clean.")
            return
            
        logger.info(f"Found {len(unprocessed)} unprocessed raw mentions to clean.")
        
        # Load all existing processed review texts to prevent duplicates
        existing_processed = db.query(ProcessedMention.brand, ProcessedMention.cleaned_text).all()
        unique_texts = {(brand, text) for brand, text in existing_processed}
        
        processed_count = 0
        skipped_lang_count = 0
        skipped_dup_count = 0
        
        for raw in unprocessed:
            cleaned = clean_text(raw.content)
            
            # Skip empty content after cleaning
            if not cleaned:
                continue
            
            # Detect language
            lang = detect_language(cleaned)
            
            # Skip if language is not English
            if lang != 'en':
                skipped_lang_count += 1
                continue
            
            # Prevent duplicate review texts per brand (deduplication check)
            if (raw.brand, cleaned) in unique_texts:
                skipped_dup_count += 1
                continue
                
            processed = ProcessedMention(
                source_id=raw.id,
                brand=raw.brand,
                source=raw.source,
                author=raw.author,
                post_date=raw.post_date,
                cleaned_text=cleaned,
                language=lang,
                sentiment_label=None,
                sentiment_score=None,
                engagement_score=raw.engagement_score
            )
            db.add(processed)
            
            # Add to local set to prevent duplicates in the same batch
            unique_texts.add((raw.brand, cleaned))
            processed_count += 1
            
        db.commit()
        logger.info(f"Cleaned: {processed_count} | Skipped (Non-English): {skipped_lang_count} | Skipped (Duplicate Text): {skipped_dup_count}")
        
    except Exception as e:
        logger.error(f"Error during cleaning pipeline: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    process_raw_mentions()
