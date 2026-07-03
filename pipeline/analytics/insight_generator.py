import os
import sys
import logging
from datetime import datetime, timezone, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from app.db.session import SessionLocal
from app.db.models.mention import ProcessedMention, AspectResult, TopicResult
from app.db.models.executive_insight import ExecutiveInsight
from analytics.ai_summarizer import generate_summary, extract_innovation_opportunities

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("insight_generator")

def get_top_risk(db, brand, since):
    from sqlalchemy import func
    
    # Top negative topic
    top_neg_topic = db.query(TopicResult.topic_name, func.count(TopicResult.id).label('c'))\
        .join(ProcessedMention)\
        .filter(ProcessedMention.brand == brand, ProcessedMention.post_date >= since, ProcessedMention.sentiment_label == 'negative')\
        .group_by(TopicResult.topic_name)\
        .order_by(func.count(TopicResult.id).desc()).first()
        
    risk = f"Negative sentiment driven by {top_neg_topic[0]}" if top_neg_topic else "No major risks detected."
    
    return risk

def get_summaries_for_fallback(db, brand, since):
    from sqlalchemy import func
    top_pos_aspect = db.query(AspectResult.aspect, func.count(AspectResult.id).label('c'))\
        .join(ProcessedMention)\
        .filter(ProcessedMention.brand == brand, ProcessedMention.post_date >= since, AspectResult.sentiment_label == 'positive')\
        .group_by(AspectResult.aspect)\
        .order_by(func.count(AspectResult.id).desc()).first()
        
    top_topic = db.query(TopicResult.topic_name, func.count(TopicResult.id).label('c'))\
        .join(ProcessedMention)\
        .filter(ProcessedMention.brand == brand, ProcessedMention.post_date >= since)\
        .group_by(TopicResult.topic_name)\
        .order_by(func.count(TopicResult.id).desc()).first()
        
    aspect_summary = f"{brand.capitalize()}'s {top_pos_aspect[0]}" if top_pos_aspect else None
    topic_summary = f"{top_topic[0]}" if top_topic else None
    
    return topic_summary, aspect_summary

def generate_insights_for_all_brands():
    logger.info("Generating Executive Insights...")
    db = SessionLocal()
    brands = ["amazon", "flipkart", "meesho", "myntra"]
    
    now = datetime.now(timezone.utc)
    one_week_ago = now - timedelta(days=7)
    
    try:
        for brand in brands:
            mentions = db.query(ProcessedMention).filter(
                ProcessedMention.brand == brand,
                ProcessedMention.post_date >= one_week_ago
            ).order_by(ProcessedMention.post_date.desc()).all()
            
            total = len(mentions)
            negative = sum(1 for m in mentions if m.sentiment_label == "negative")
            neg_ratio = (negative / total * 100) if total > 0 else 0
            
            risk = get_top_risk(db, brand, one_week_ago)
            topic_summary, aspect_summary = get_summaries_for_fallback(db, brand, one_week_ago)
            
            reviews_texts = [m.cleaned_text for m in mentions[:100] if m.cleaned_text]
            opp_data = extract_innovation_opportunities(reviews_texts, brand, topic_summary, aspect_summary)
            
            data_dict = {
                "brand": brand,
                "total_mentions": total,
                "negative_ratio": neg_ratio,
                "top_risk": risk,
                "top_opportunity": opp_data.get("summary", "")
            }
            
            summary = generate_summary(data_dict)
            
            # Persist
            insight = ExecutiveInsight(
                brand=brand,
                top_risk=risk,
                top_opportunity=opp_data.get("summary", ""), # legacy column
                top_opportunity_summary=opp_data.get("summary", ""),
                top_opportunity_json=opp_data,
                executive_summary=summary,
                generated_at=now
            )
            db.add(insight)
            logger.info(f"Generated insight for {brand}.")
            
        db.commit()
    except Exception as e:
        logger.error(f"Insight generation failed: {e}")
        db.rollback()
    finally:
        db.close()
    
    logger.info("Finished generating Executive Insights.")

if __name__ == "__main__":
    generate_insights_for_all_brands()
