import sys
import os
import logging
from google_play_scraper import reviews, Sort

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("playstore_collector")

# Add backend to path to import DB connection and models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from app.db.session import SessionLocal
from app.db.models.mention import RawMention

# App package IDs on Play Store
APPS = {
    "amazon": "com.amazon.mShop.android.shopping",
    "flipkart": "com.flipkart.android",
    "meesho": "com.meesho.supply",
    "myntra": "com.myntra.android"
}

def collect_playstore_reviews(count: int = 100):
    db = SessionLocal()
    try:
        for brand, app_id in APPS.items():
            logger.info(f"Starting Play Store review collection for {brand} ({app_id})...")
            try:
                # Fetch reviews from google-play-scraper
                result, _ = reviews(
                    app_id,
                    lang='en',
                    country='in',  # Target Indian market reviews
                    sort=Sort.NEWEST,
                    count=count
                )
                
                logger.info(f"Successfully fetched {len(result)} reviews from Play Store for {brand}")
                
                inserted_count = 0
                for r in result:
                    # Check for duplicate in raw_mentions by matching external_id
                    existing = db.query(RawMention).filter(
                        RawMention.external_id == r['reviewId']
                    ).first()
                    
                    if not existing:
                        mention = RawMention(
                            brand=brand,
                            source='playstore',
                            external_id=r['reviewId'],
                            content=r['content'],
                            rating=float(r['score']),
                            author=r['userName'],
                            post_date=r['at'],
                            engagement_score=r.get('thumbsUpCount', 0)
                        )

                        db.add(mention)
                        inserted_count += 1
                
                db.commit()
                logger.info(f"Inserted {inserted_count} new raw mentions for {brand}")
                
            except Exception as e:
                logger.error(f"Error collecting reviews for {brand}: {e}")
                db.rollback()
                
    finally:
        db.close()

if __name__ == "__main__":
    collect_playstore_reviews(100)
