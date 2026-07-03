import sys
import os
import logging
from datetime import datetime, timezone

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("reddit_collector")

# Add backend to path to import DB connection and models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

from app.db.session import SessionLocal
from app.db.models.mention import RawMention

def get_praw_client():
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "social-intelligence-bot")
    
    # Check if they are empty or placeholder values
    if not client_id or "placeholder" in client_id.lower() or "your_reddit" in client_id.lower():
        logger.warning("REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET are placeholder values. Falling back to Mock Data mode.")
        return None
        
    try:
        import praw
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        # Verify read-only access
        reddit.read_only = True
        # Perform a quick read-only test
        list(reddit.subreddit("test").new(limit=1))
        logger.info("Successfully authenticated with Reddit API using PRAW.")
        return reddit
    except Exception as e:
        logger.warning(f"Failed to authenticate with Reddit API: {e}. Falling back to Mock Data mode.")
        return None

def get_mock_reddit_data():
    logger.info("Generating realistic mock Reddit posts for Amazon, Flipkart, Meesho, and Myntra...")
    now = datetime.now(timezone.utc)
    return [
        # Amazon Mock Reviews
        {
            "id": "mock_red_amz_01",
            "brand": "amazon",
            "title": "Amazon Prime delivery is getting slower",
            "selftext": "Remember when Prime meant next-day delivery guaranteed? Now even in metro cities it takes 3-4 days. Plus the price of the Prime subscription has gone up. Highly disappointed.",
            "author": "u/prime_shopper",
            "created_utc": now.timestamp() - 3600 * 2,
            "engagement_score": 145
        },
        {
            "id": "mock_red_amz_02",
            "brand": "amazon",
            "title": "Ordered a phone and received a brick! Support resolved it though",
            "selftext": "Ordered a brand new OnePlus phone during the sale and got a brick inside a sealed package. Extremely shocked! Luckily customer support verified the weight discrepancy and initiated a replacement.",
            "author": "u/lucky_brick",
            "created_utc": now.timestamp() - 3600 * 12,
            "engagement_score": 890
        },
        {
            "id": "mock_red_amz_03",
            "brand": "amazon",
            "title": "Great price and discount on groceries today",
            "selftext": "Got a great coupon deal on Amazon Fresh grocery shopping today. Delivered within 3 hours, packaging was very clean and items were fresh.",
            "author": "u/daily_savings",
            "created_utc": now.timestamp() - 3600 * 5,
            "engagement_score": 32
        },
        
        # Flipkart Mock Reviews
        {
            "id": "mock_red_fk_01",
            "brand": "flipkart",
            "title": "Flipkart Plus membership is not worth it anymore",
            "selftext": "Supercoins are practically useless now and they have added a secure packaging fee on everything. Value for money is completely gone.",
            "author": "u/supercoin_hoarder",
            "created_utc": now.timestamp() - 3600 * 4,
            "engagement_score": 520
        },
        {
            "id": "mock_red_fk_02",
            "brand": "flipkart",
            "title": "Delivery agent misbehaved and the box was torn open",
            "selftext": "The delivery boy was shouting and demanding cash even though I paid online. To make it worse, the package was damaged and taped up badly. Disastrous delivery service.",
            "author": "u/delivery_nightmare",
            "created_utc": now.timestamp() - 3600 * 18,
            "engagement_score": 1120
        },
        {
            "id": "mock_red_fk_03",
            "brand": "flipkart",
            "title": "Received fake shoes from a certified seller",
            "selftext": "Ordered running shoes and received a cheap duplicate copy. The stitching was coming off and the logo looked wrong. Initiated a return request immediately.",
            "author": "u/sports_junkie",
            "created_utc": now.timestamp() - 3600 * 20,
            "engagement_score": 75
        },

        # Meesho Mock Reviews
        {
            "id": "mock_red_ms_01",
            "brand": "meesho",
            "title": "Meesho prices are cheap but product quality is a gamble",
            "selftext": "Got a t-shirt for 150 rupees, which is cheap, but the fabric quality is very thin and synthetic. You get what you pay for.",
            "author": "u/budget_shopper",
            "created_utc": now.timestamp() - 3600 * 6,
            "engagement_score": 45
        },
        {
            "id": "mock_red_ms_02",
            "brand": "meesho",
            "title": "Meesho app UX is very laggy on budget phones",
            "selftext": "The app takes ages to load images and crashes during checkout. Navigation is painful and UI feels extremely slow.",
            "author": "u/android_guy",
            "created_utc": now.timestamp() - 3600 * 24,
            "engagement_score": 210
        },
        {
            "id": "mock_red_ms_03",
            "brand": "meesho",
            "title": "Return request got cancelled without reason",
            "selftext": "Tried returning a damaged bag I received. The system automatically cancelled my return request twice saying 'pickup failed' when no agent ever contacted me. Disastrous support.",
            "author": "u/scammed_customer",
            "created_utc": now.timestamp() - 3600 * 48,
            "engagement_score": 430
        },

        # Myntra Mock Reviews
        {
            "id": "mock_red_myn_01",
            "brand": "myntra",
            "title": "Myntra Insider points are awesome for deals",
            "selftext": "Used my Myntra Insider points to get a flat 300 off coupon on a jacket. Myntra delivery is always super fast and packing is clean.",
            "author": "u/fashion_trends",
            "created_utc": now.timestamp() - 3600 * 8,
            "engagement_score": 110
        },
        {
            "id": "mock_red_myn_02",
            "brand": "myntra",
            "title": "Size is too tight, but return policy is very smooth",
            "selftext": "The shirt quality is great but it fits too tight around the chest. The exchange process was very smooth, they picked it up and delivered the next size in 2 days.",
            "author": "u/style_guide",
            "created_utc": now.timestamp() - 3600 * 15,
            "engagement_score": 22
        },
        {
            "id": "mock_red_myn_03",
            "brand": "myntra",
            "title": "App crashed during payment, money deducted",
            "selftext": "Was paying via UPI and the Myntra app crashed. The money got debited from my bank but the order wasn't placed. Customer care agent says refund will take 7 business days, very annoying app bug.",
            "author": "u/unlucky_buyer",
            "created_utc": now.timestamp() - 3600 * 30,
            "engagement_score": 380
        }
    ]

def collect_reddit_via_playwright(limit: int = 50) -> list[dict]:
    from playwright.sync_api import sync_playwright
    import time
    import json
    
    brands = ["amazon", "flipkart", "meesho", "myntra"]
    results = []
    
    with sync_playwright() as p:
        logger.info("Launching headless browser for Reddit Playwright scraping fallback...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        
        for brand in brands:
            page = context.new_page()
            url = f"https://www.reddit.com/search/?q={brand}&sort=new"
            logger.info(f"Navigating to Reddit search for '{brand}': {url}")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3000)
                
                trackers = page.locator("search-telemetry-tracker").all()
                logger.info(f"Found {len(trackers)} search-telemetry-tracker items for '{brand}'")
                
                brand_count = 0
                for t in trackers:
                    if brand_count >= limit:
                        break
                        
                    context_str = t.get_attribute("data-faceplate-tracking-context") or ""
                    if not context_str:
                        continue
                    try:
                        context_data = json.loads(context_str)
                        post_info = context_data.get("post", {})
                        profile_info = context_data.get("profile", {})
                        if not post_info:
                            continue
                            
                        raw_id = post_info.get("id", "")
                        clean_id = raw_id.replace("t3_", "") if raw_id.startswith("t3_") else raw_id
                        if not clean_id:
                            continue
                            
                        title = post_info.get("title", "")
                        author_name = profile_info.get("name", "anonymous")
                        author = f"u/{author_name}" if not author_name.startswith("u/") else author_name
                        
                        # Timeago / datetime string
                        time_el = t.locator("faceplate-timeago")
                        created_utc = time.time()
                        if time_el.count() > 0:
                            time_el_time = time_el.first.locator("time")
                            if time_el_time.count() > 0:
                                dt_str = time_el_time.first.get_attribute("datetime") or ""
                                if dt_str:
                                    try:
                                        clean_str = dt_str.replace("Z", "+00:00")
                                        created_utc = datetime.fromisoformat(clean_str).timestamp()
                                    except Exception:
                                        pass
                                        
                        # Selftext snippet
                        snippet = ""
                        snippet_el = t.locator("div[class*='text-neutral-content'] p, p[class*='text-neutral-content']")
                        if snippet_el.count() > 0:
                            snippet = snippet_el.first.inner_text().strip()
                        else:
                            p_elements = t.locator("p").all()
                            for p_el in p_elements:
                                p_text = p_el.inner_text().strip()
                                if p_text and p_text != title and not p_text.startswith("r/") and not p_text.endswith("ago"):
                                    snippet = p_text
                                    break
                                    
                        # Try to get score
                        score = post_info.get("score") or post_info.get("upvoteCount") or 0
                        try:
                            score = int(score)
                        except:
                            score = 0

                        results.append({
                            "id": clean_id,
                            "brand": brand,
                            "title": title,
                            "selftext": snippet,
                            "author": author,
                            "created_utc": created_utc,
                            "engagement_score": score
                        })
                        brand_count += 1
                    except Exception as json_err:
                        logger.debug(f"Failed to parse post JSON: {json_err}")
                        
                logger.info(f"Collected {brand_count} posts for '{brand}' using Playwright.")
            except Exception as page_err:
                logger.error(f"Error navigating/scraping Reddit search for '{brand}': {page_err}")
            finally:
                page.close()
                
        browser.close()
    return results

def collect_reddit_reviews(limit: int = 50):
    db = SessionLocal()
    try:
        reddit = get_praw_client()
        
        results = []
        if reddit:
            brands = ["amazon", "flipkart", "meesho", "myntra"]
            for brand in brands:
                logger.info(f"Searching Reddit for '{brand}' mentions...")
                # Search across all of Reddit
                search_results = reddit.subreddit("all").search(brand, sort="new", limit=limit)
                for post in search_results:
                    results.append({
                        "id": post.id,
                        "brand": brand,
                        "title": post.title,
                        "selftext": post.selftext or "",
                        "author": f"u/{post.author.name}" if post.author else "u/anonymous",
                        "created_utc": post.created_utc,
                        "engagement_score": post.score
                    })
                
                # Fetch recent from specific subreddits if they exist
                logger.info(f"Fetching recent posts from r/{brand} subreddit...")
                try:
                    subreddit_posts = reddit.subreddit(brand).new(limit=limit)
                    for post in subreddit_posts:
                        results.append({
                            "id": post.id,
                            "brand": brand,
                            "title": post.title,
                            "selftext": post.selftext or "",
                            "author": f"u/{post.author.name}" if post.author else "u/anonymous",
                            "created_utc": post.created_utc,
                            "engagement_score": post.score
                        })
                except Exception as sub_err:
                    logger.warning(f"Could not fetch r/{brand} subreddit posts: {sub_err}")
        else:
            # Fall back to Playwright scraping fallback first
            logger.info("PRAW Reddit API is not configured. Falling back to Playwright web scraping...")
            try:
                results = collect_reddit_via_playwright(limit=limit)
            except Exception as pw_err:
                logger.error(f"Playwright scraping failed: {pw_err}. Falling back to static mock data.")
                results = []
                
            if not results:
                logger.info("No live posts collected via Playwright. Loading static mock data...")
                results = get_mock_reddit_data()
            
        # 3. Store in DB
        logger.info(f"Processing and inserting {len(results)} Reddit raw mentions into database...")
        inserted_count = 0
        seen_ids = set()
        for item in results:
            ext_id = f"reddit_post_{item['id']}"
            
            if ext_id in seen_ids:
                continue
            seen_ids.add(ext_id)
            
            # Check for duplicates in raw_mentions
            existing = db.query(RawMention).filter(RawMention.external_id == ext_id).first()
            
            if not existing:
                # Calculate rating heuristic if absent
                rating = None
                
                mention = RawMention(
                    brand=item["brand"],
                    source="reddit",
                    external_id=ext_id,
                    content=f"{item['title']}. {item['selftext']}",
                    author=item["author"],
                    post_date=datetime.fromtimestamp(item["created_utc"], timezone.utc),
                    rating=rating,
                    engagement_score=item.get("engagement_score", 0)
                )
                db.add(mention)
                inserted_count += 1
                
        db.commit()
        logger.info(f"Ingestion complete. Saved {inserted_count} new raw Reddit mentions to the database.")
        
    except Exception as e:
        logger.error(f"Error collecting Reddit data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    collect_reddit_reviews(50)

