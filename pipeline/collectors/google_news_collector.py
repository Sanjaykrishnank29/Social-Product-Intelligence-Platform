import sys
import os
import logging
import feedparser
import time
from datetime import datetime, timezone
from urllib.parse import quote

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("google_news_collector")

# Add backend to path to import DB connection and models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from app.db.session import SessionLocal
from app.db.models.mention import RawMention

BRANDS = ["amazon", "flipkart", "meesho", "myntra"]

def collect_google_news(limit_per_brand: int = 30):
    db = SessionLocal()
    try:
        for brand in BRANDS:
            logger.info(f"Starting Google News collection for '{brand}'...")
            
            # Query for English news in India targeting the brand
            query = quote(f"{brand} india")
            rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
            
            logger.info(f"Parsing RSS feed: {rss_url}")
            feed = feedparser.parse(rss_url)
            
            entries = feed.entries[:limit_per_brand]
            logger.info(f"Found {len(entries)} entries in RSS feed for {brand}")
            
            inserted_count = 0
            for entry in entries:
                # Deduplication check by matching link
                link = entry.get("link")
                if not link:
                    continue
                
                existing = db.query(RawMention).filter(
                    RawMention.external_id == link
                ).first()
                
                if not existing:
                    # Parse publish date
                    if entry.get("published_parsed"):
                        post_dt = datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
                    else:
                        post_dt = datetime.now(timezone.utc)
                        
                    # Extract publisher/source name
                    source_info = entry.get("source", {})
                    author = source_info.get("title", "Google News")
                    
                    # Content consists of the title + description/summary
                    title = entry.get("title", "")
                    summary = entry.get("summary", "")
                    content_text = f"{title}\n{summary}".strip()
                    
                    mention = RawMention(
                        brand=brand,
                        source='google_news',
                        external_id=link,
                        content=content_text,
                        rating=None,  # News articles do not have a 1-5 rating
                        author=author,
                        post_date=post_dt,
                        engagement_score=0
                    )
                    db.add(mention)
                    inserted_count += 1
            
            db.commit()
            logger.info(f"Successfully saved {inserted_count} new raw news mentions for {brand}")
            
    except Exception as e:
        logger.error(f"Error collecting Google News data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    collect_google_news(30)
