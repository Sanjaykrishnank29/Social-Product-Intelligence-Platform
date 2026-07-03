import sys
import os
import re
import logging
import hashlib
import time
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("google_store_collector")

# Add backend to path to import DB connection and models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from app.db.session import SessionLocal
from app.db.models.mention import RawMention

BRANDS_URLS = {
    "amazon": "https://www.google.com/storepages?q=amazon.com&c=US&v=19",
    "flipkart": "https://www.google.com/storepages?q=flipkart.com&c=US&v=19",
    "meesho": "https://www.google.com/storepages?q=meesho.com&c=US&v=19",
    "myntra": "https://www.google.com/storepages?q=myntra.com&c=US&v=19"
}

def clean_html(raw_html):
    # Strip HTML tags
    clean = re.sub(r'<.*?>', '', raw_html)
    clean = clean.replace('&quot;', '"').replace('&#39;', "'").replace('&amp;', '&').replace('&gt;', '>').replace('&lt;', '<')
    return re.sub(r'\s+', ' ', clean).strip()

def parse_date(date_str):
    if not date_str:
        return datetime.now(timezone.utc)
    # E.g. "Dec 18, 2025 on Google" or "Jan 11 on Google" or "4 weeks ago on Google"
    # Clean string
    clean_str = date_str.replace("on Google", "").strip()
    try:
        # Simple date string mapping
        # If it says "X weeks/days ago", approximate it
        if "ago" in clean_str:
            num = int(re.search(r'\d+', clean_str).group())
            if "week" in clean_str:
                return datetime.fromtimestamp(time.time() - num * 7 * 86400, tz=timezone.utc)
            elif "day" in clean_str:
                return datetime.fromtimestamp(time.time() - num * 86400, tz=timezone.utc)
            elif "month" in clean_str:
                return datetime.fromtimestamp(time.time() - num * 30 * 86400, tz=timezone.utc)
        
        # If year is missing, assume current year
        parts = clean_str.split(",")
        if len(parts) == 1:
            clean_str = f"{clean_str}, {datetime.now().year}"
            
        # Parse month day, year format
        return datetime.strptime(clean_str, "%b %d, %Y").replace(tzinfo=timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)

def collect_google_store_reviews():
    db = SessionLocal()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        
        try:
            for brand, url in BRANDS_URLS.items():
                logger.info(f"Opening Google Storepage for {brand}: {url}")
                page = context.new_page()
                
                try:
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    html_content = page.content()
                    
                    # Parse reviews using robust regex matching
                    # Google uses either single/double quotes or HTML-escaped quotes (&#39; or ')
                    review_blocks = re.findall(
                        r'aria-label="Star icons representing the user(?:&#39;|\')s review of the merchant which is ([\d\.]+) out of 5." role="img".*?<p class="[^"]*?-jRmmHf">([^<]+?)</p>.*?<p class="[^"]*?-jNm5if">(.*?)</p>',
                        html_content,
                        re.DOTALL
                    )
                    
                    logger.info(f"Found {len(review_blocks)} Google Store reviews for {brand}")
                    
                    inserted_count = 0
                    for rating_str, date_str, body in review_blocks:
                        content_text = clean_html(body)
                        if not content_text:
                            continue
                            
                        # Generate content-based deduplication hash
                        content_hash = hashlib.md5(content_text.encode('utf-8')).hexdigest()
                        external_id = f"google_store_{brand}_{content_hash}"
                        
                        # Check for duplicates
                        existing = db.query(RawMention).filter(
                            RawMention.external_id == external_id
                        ).first()
                        
                        if not existing:
                            rating = float(rating_str) if rating_str is not None else None
                            post_date = parse_date(date_str)
                            
                            mention = RawMention(
                                brand=brand,
                                source='google_store',
                                external_id=external_id,
                                content=content_text,
                                rating=rating,
                                author="Google User",
                                post_date=post_date,
                                engagement_score=0
                            )
                            db.add(mention)
                            inserted_count += 1
                            
                    db.commit()
                    logger.info(f"Successfully saved {inserted_count} new raw Google Store reviews for {brand}")
                    
                except Exception as page_err:
                    logger.error(f"Error processing page for {brand}: {page_err}")
                finally:
                    page.close()
                    
        finally:
            browser.close()
            db.close()

if __name__ == "__main__":
    collect_google_store_reviews()
