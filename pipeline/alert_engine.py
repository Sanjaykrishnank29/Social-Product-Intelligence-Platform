import os
import sys
import logging
from datetime import datetime, timezone, timedelta
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.db.session import SessionLocal
from app.db.models.alert_log import AlertLog
from app.db.models.mention import ProcessedMention, TopicResult
from sqlalchemy import func

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("alert_engine")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_alert(db, alert_type, brand, severity, message):
    alert = AlertLog(
        alert_type=alert_type,
        brand=brand,
        severity=severity,
        message=message,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(alert)
    db.commit()
    logger.info(f"ALERT LOGGED [{severity}] {brand} ({alert_type}): {message}")

    if SLACK_WEBHOOK_URL:
        try:
            requests.post(SLACK_WEBHOOK_URL, json={"text": f"[{severity}] {brand.upper()}: {message}"}, timeout=5)
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

def check_sentiment_spikes(db, brands):
    now = datetime.now(timezone.utc)
    twenty_four_hours_ago = now - timedelta(hours=24)
    
    for brand in brands:
        mentions = db.query(ProcessedMention).filter(
            ProcessedMention.brand == brand,
            ProcessedMention.post_date >= twenty_four_hours_ago
        ).all()
        
        total = len(mentions)
        if total >= 20:
            negative = sum(1 for m in mentions if m.sentiment_label == "negative")
            ratio = negative / total
            if ratio >= 0.5:
                send_alert(
                    db,
                    alert_type="sentiment_spike",
                    brand=brand,
                    severity="HIGH",
                    message=f"Negative sentiment spike detected! {ratio*100:.1f}% of {total} mentions in the last 24h were negative."
                )

def check_topic_surges(db, brands):
    now = datetime.now(timezone.utc)
    twenty_four_hours_ago = now - timedelta(hours=24)
    forty_eight_hours_ago = now - timedelta(hours=48)
    
    # We use keywords to find matches in TopicResult.topic_name
    critical_topics = ['refund', 'delivery', 'payment', 'customer support']
    
    for brand in brands:
        for topic in critical_topics:
            current_count = db.query(TopicResult).join(ProcessedMention).filter(
                ProcessedMention.brand == brand,
                ProcessedMention.post_date >= twenty_four_hours_ago,
                TopicResult.topic_name.ilike(f"%{topic}%")
            ).count()
            
            previous_count = db.query(TopicResult).join(ProcessedMention).filter(
                ProcessedMention.brand == brand,
                ProcessedMention.post_date >= forty_eight_hours_ago,
                ProcessedMention.post_date < twenty_four_hours_ago,
                TopicResult.topic_name.ilike(f"%{topic}%")
            ).count()
            
            # Surge logic: > 50% increase AND minimum 5 mentions
            if current_count >= 5 and current_count > (previous_count * 1.5):
                send_alert(
                    db,
                    alert_type="topic_surge",
                    brand=brand,
                    severity="MEDIUM",
                    message=f"Topic Surge: '{topic}' increased from {previous_count} to {current_count} mentions in the last 24h."
                )

def check_all_alerts():
    logger.info("Running Alert Engine...")
    db = SessionLocal()
    try:
        brands = ["amazon", "flipkart", "meesho", "myntra"]
        check_sentiment_spikes(db, brands)
        check_topic_surges(db, brands)
    finally:
        db.close()
    logger.info("Alert Engine checks complete.")

if __name__ == "__main__":
    check_all_alerts()
