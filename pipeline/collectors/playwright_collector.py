import sys
import os
import json
import logging
import time
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("playwright_collector")

# Add backend to path to import DB connection and models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from app.db.session import SessionLocal
from app.db.models.mention import RawMention

BRANDS_URLS = {
    "amazon": "https://www.trustpilot.com/review/www.amazon.in",
    "flipkart": "https://www.trustpilot.com/review/www.flipkart.com",
    "meesho": "https://www.trustpilot.com/review/www.meesho.com",
    "myntra": "https://www.trustpilot.com/review/www.myntra.com"
}

def find_reviews_in_json(obj):
    if isinstance(obj, dict):
        if "reviews" in obj and isinstance(obj["reviews"], list) and len(obj["reviews"]) > 0:
            # Check if it has expected review keys (like text or rating or consumer)
            first_item = obj["reviews"][0]
            if isinstance(first_item, dict) and ("text" in first_item or "rating" in first_item or "id" in first_item):
                return obj["reviews"]
        for k, v in obj.items():
            res = find_reviews_in_json(v)
            if res is not None:
                return res
    elif isinstance(obj, list):
        for item in obj:
            res = find_reviews_in_json(item)
            if res is not None:
                return res
    return None

def parse_date(date_str):
    if not date_str:
        return datetime.now(timezone.utc)
    try:
        # Trustpilot dates are usually ISO strings (e.g. "2026-06-11T10:00:00.000Z")
        # Replace Z with UTC offset
        clean_str = date_str.replace("Z", "+00:00")
        return datetime.fromisoformat(clean_str)
    except Exception:
        return datetime.now(timezone.utc)

def collect_trustpilot_reviews():
    db = SessionLocal()
    
    with sync_playwright() as p:
        # Launch browser with custom user agent and headless mode
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        
        try:
            for brand, url in BRANDS_URLS.items():
                logger.info(f"Opening Trustpilot page for {brand}: {url}")
                page = context.new_page()
                
                try:
                    # Navigate with networkidle state to wait for dynamic scripts to load
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    
                    # Method 1: Extract __NEXT_DATA__ tag
                    logger.info("Attempting to parse next_data JSON state...")
                    script_tag = page.locator("script#__NEXT_DATA__")
                    
                    reviews_data = None
                    if script_tag.count() > 0:
                        json_content = script_tag.text_content()
                        if json_content:
                            try:
                                full_json = json.loads(json_content)
                                reviews_data = find_reviews_in_json(full_json)
                            except Exception as json_err:
                                logger.error(f"Error parsing next_data JSON: {json_err}")
                                
                    # Process structured reviews from JSON
                    if reviews_data:
                        logger.info(f"Found {len(reviews_data)} reviews in JSON state for {brand}")
                        inserted_count = 0
                        for r in reviews_data:
                            review_id = r.get("id") or r.get("reviewId")
                            if not review_id:
                                continue
                            
                            external_id = f"trustpilot_{review_id}"
                            
                            # Check for duplicates
                            existing = db.query(RawMention).filter(
                                RawMention.external_id == external_id
                            ).first()
                            
                            if not existing:
                                # Extract rating, text, and date
                                rating_val = r.get("rating") or r.get("stars") or r.get("score")
                                rating = float(rating_val) if rating_val is not None else None
                                
                                title = r.get("title") or ""
                                body = r.get("text") or r.get("content") or r.get("body") or ""
                                content_text = f"{title}\n{body}".strip()
                                
                                # Skip empty reviews
                                if not content_text:
                                    continue
                                
                                author = r.get("consumer", {}).get("displayName") or r.get("userName") or "Anonymous"
                                date_str = r.get("dates", {}).get("publishedDate") or r.get("createdAt") or r.get("date")
                                post_date = parse_date(date_str)
                                
                                mention = RawMention(
                                    brand=brand,
                                    source='trustpilot',
                                    external_id=external_id,
                                    content=content_text,
                                    rating=rating,
                                    author=author,
                                    post_date=post_date,
                                    engagement_score=int(r.get("likes") or r.get("upvotes") or r.get("usefulCount") or 0)
                                )
                                db.add(mention)
                                inserted_count += 1
                        
                        db.commit()
                        logger.info(f"Successfully inserted {inserted_count} Trustpilot reviews for {brand}")
                        
                    else:
                        # Method 2 Fallback: Basic DOM selectors
                        logger.warning("NEXT_DATA reviews not found. Falling back to DOM parsing...")
                        review_elements = page.locator("article").all()
                        logger.info(f"Found {len(review_elements)} article elements on page")
                        
                        inserted_count = 0
                        for index, article in enumerate(review_elements):
                            try:
                                # Get a unique ID or use index
                                raw_text = article.inner_text() or ""
                                if not raw_text.strip():
                                    continue
                                
                                external_id = f"trustpilot_dom_{brand}_{index}_{int(time.time())}"
                                
                                # Try extracting rating from attributes or child stars
                                rating = None
                                rating_div = article.locator("div[data-service-review-rating]")
                                if rating_div.count() > 0:
                                    val = rating_div.first.get_attribute("data-service-review-rating")
                                    if val:
                                        rating = float(val)
                                        
                                # Try extracting author
                                author = "Anonymous"
                                author_span = article.locator('span[class*="typography_heading-xxs"]')
                                if author_span.count() > 0:
                                    author = author_span.first.inner_text() or "Anonymous"
                                    
                                # Review body text
                                body = ""
                                body_p = article.locator('p[data-service-review-text-typography]')
                                if body_p.count() > 0:
                                    body = body_p.first.inner_text() or ""
                                    
                                if not body:
                                    body = raw_text
                                    
                                mention = RawMention(
                                    brand=brand,
                                    source='trustpilot',
                                    external_id=external_id,
                                    content=body.strip(),
                                    rating=rating,
                                    author=author.strip(),
                                    post_date=datetime.now(timezone.utc),
                                    engagement_score=0
                                )
                                db.add(mention)
                                inserted_count += 1
                                
                            except Exception as element_err:
                                logger.error(f"Error parsing DOM element: {element_err}")
                                
                        db.commit()
                        logger.info(f"DOM parsing: successfully inserted {inserted_count} Trustpilot reviews for {brand}")
                        
                except Exception as page_err:
                    logger.error(f"Error page processing for {brand}: {page_err}")
                finally:
                    page.close()
                    
        finally:
            browser.close()
            db.close()

if __name__ == "__main__":
    collect_trustpilot_reviews()
