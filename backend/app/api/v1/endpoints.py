from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.db.models.mention import RawMention, ProcessedMention, AspectResult, TopicResult
from app.core.logging import logger
from typing import Optional, List
from elasticsearch import Elasticsearch
from app.core.config import settings
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter()

ASPECTS = ["delivery_packaging", "product_quality", "price_value", "returns_refunds", "app_ux"]
INDEX_NAME = "processed_mentions"

def get_all_brands(db: Session) -> list[str]:
    brands = db.query(ProcessedMention.brand).distinct().order_by(ProcessedMention.brand).all()
    return [b[0] for b in brands]

es = Elasticsearch(settings.ELASTICSEARCH_URL)

@router.get("/health")
def health():
    logger.info("Health check endpoint hit")
    return {"status": "healthy"}

@router.get("/brands")
def get_brands(db: Session = Depends(get_db)):
    logger.info("Retrieving available brands")
    return {"status": "success", "brands": get_all_brands(db)}

@router.get("/brands/{brand}")
def get_brand_details(brand: str, db: Session = Depends(get_db)):
    logger.info(f"Retrieving details for brand: {brand}")
    brand_lower = brand.lower()
    
    # 1. Volume and Rating
    raw_stats = db.query(
        func.count(RawMention.id).label("total_volume"),
        func.avg(RawMention.rating).label("avg_rating")
    ).filter(RawMention.brand == brand_lower).first()
    
    volume = raw_stats.total_volume or 0
    rating = round(float(raw_stats.avg_rating or 0), 1)
    
    # 2. Sentiment
    sent_stats = db.query(
        ProcessedMention.sentiment_label,
        func.count(ProcessedMention.id).label("count")
    ).filter(ProcessedMention.brand == brand_lower, ProcessedMention.sentiment_label != None).group_by(ProcessedMention.sentiment_label).all()
    
    sentiment = {"positive": 0, "neutral": 0, "negative": 0}
    for stat in sent_stats:
        sentiment[stat.sentiment_label] = stat.count
        
    total_sent = sum(sentiment.values())
    pos_ratio = (sentiment["positive"] / total_sent * 100) if total_sent > 0 else 0
    neg_ratio = (sentiment["negative"] / total_sent * 100) if total_sent > 0 else 0
    net_sentiment = pos_ratio - neg_ratio
    
    # 3. Overall Score Calculation
    # Normalize components to 0-100 scale
    norm_sentiment = (net_sentiment + 100) / 2  # -100..100 -> 0..100
    norm_rating = (rating / 5) * 100
    
    # To normalize volume, get max volume across all brands
    max_volume = db.query(func.count(RawMention.id)).group_by(RawMention.brand).order_by(func.count(RawMention.id).desc()).limit(1).scalar() or 1
    norm_volume = (volume / max_volume) * 100
    
    norm_trend = 50.0  # Default middle ground for trend until time-series is implemented
    
    overall_score = (0.4 * norm_sentiment) + (0.3 * norm_rating) + (0.2 * norm_volume) + (0.1 * norm_trend)
    
    # 4. Executive Insights
    from app.db.models.executive_insight import ExecutiveInsight
    insight = db.query(ExecutiveInsight).filter(ExecutiveInsight.brand == brand_lower).order_by(ExecutiveInsight.generated_at.desc()).first()
    
    # 5. Recent Alerts
    from app.db.models.alert_log import AlertLog
    alerts = db.query(AlertLog).filter(AlertLog.brand == brand_lower).order_by(AlertLog.timestamp.desc()).limit(5).all()
    
    return {
        "brand": brand_lower,
        "score": round(overall_score),
        "mentions": volume,
        "rating": rating,
        "sentiment": sentiment,
        "top_risk": insight.top_risk if insight else "No sufficient data to identify top risk yet.",
        "top_opportunity": insight.top_opportunity_summary or insight.top_opportunity if insight else "No sufficient data to identify top opportunity yet.",
        "executive_summary": insight.executive_summary if insight else "Brand analysis is still gathering data.",
        "recent_alerts": [
            {
                "id": a.id,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "timestamp": a.timestamp.isoformat() if a.timestamp else None
            } for a in alerts
        ]
    }

@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    logger.info("Retrieving brand overview metrics")
    
    # Volumes and Avg ratings from raw_mentions
    raw_stats = db.query(
        RawMention.brand,
        func.count(RawMention.id).label("total_volume"),
        func.avg(RawMention.rating).label("avg_rating")
    ).group_by(RawMention.brand).all()
    
    # Sentiment counts from processed_mentions
    sentiment_stats = db.query(
        ProcessedMention.brand,
        ProcessedMention.sentiment_label,
        func.count(ProcessedMention.id).label("count")
    ).group_by(ProcessedMention.brand, ProcessedMention.sentiment_label).all()
    
    # Structure the response
    brand_overview = {}
    db_brands = get_all_brands(db)
    for brand in db_brands:
        brand_overview[brand] = {
            "total_volume": 0,
            "avg_rating": 0.0,
            "sentiment": {"positive": 0, "neutral": 0, "negative": 0}
        }
        
    for stat in raw_stats:
        b = stat.brand.lower()
        if b in brand_overview:
            brand_overview[b]["total_volume"] = stat.total_volume
            brand_overview[b]["avg_rating"] = round(float(stat.avg_rating or 0), 2)
            
    for stat in sentiment_stats:
        b = stat.brand.lower()
        label = stat.sentiment_label
        if b in brand_overview and label:
            brand_overview[b]["sentiment"][label] = stat.count
            
    return brand_overview

@router.get("/sentiment")
def get_sentiment_stats(db: Session = Depends(get_db)):
    logger.info("Retrieving detailed sentiment statistics")
    # Retrieve total processed counts and distributions
    stats = db.query(
        ProcessedMention.brand,
        ProcessedMention.sentiment_label,
        func.count(ProcessedMention.id).label("count")
    ).filter(ProcessedMention.sentiment_label != None).group_by(
        ProcessedMention.brand, ProcessedMention.sentiment_label
    ).all()
    
    db_brands = get_all_brands(db)
    distribution = {b: {} for b in db_brands}
    for stat in stats:
        b = stat.brand.lower()
        if b in distribution:
            distribution[b][stat.sentiment_label] = stat.count
            
    return distribution

@router.get("/feed")
def get_reviews_feed(
    brand: Optional[str] = Query(None, description="Filter by brand (amazon, flipkart, meesho, myntra)"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment (positive, neutral, negative)"),
    source: Optional[str] = Query(None, description="Filter by source (playstore, reddit, google_news, trustpilot, google_store)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    logger.info(f"Retrieving reviews feed: brand={brand}, sentiment={sentiment}, source={source}, skip={skip}, limit={limit}")
    
    query = db.query(ProcessedMention)
    if brand:
        query = query.filter(ProcessedMention.brand == brand.lower())
    if sentiment:
        query = query.filter(ProcessedMention.sentiment_label == sentiment.lower())
    if source:
        query = query.filter(ProcessedMention.source == source.lower())
        
    total_count = query.count()
    results = query.order_by(ProcessedMention.post_date.desc()).offset(skip).limit(limit).all()
    
    feed_items = []
    for item in results:
        feed_items.append({
            "id": item.id,
            "brand": item.brand,
            "source": item.source,
            "author": item.author,
            "post_date": item.post_date,
            "cleaned_text": item.cleaned_text,
            "sentiment_label": item.sentiment_label,
            "sentiment_score": round(float(item.sentiment_score or 0), 4) if item.sentiment_score else None
        })
        
    return {
        "total": total_count,
        "skip": skip,
        "limit": limit,
        "items": feed_items
    }

@router.get("/compare")
def get_comparison(brands: str = Query(..., description="Comma separated list of brands"), db: Session = Depends(get_db)):
    logger.info("Retrieving brand comparison metrics")
    
    brand_list = [b.strip().lower() for b in brands.split(",")]
    overview = get_overview(db)
    
    def calc_ratio(sentiment_dict, label):
        total = sum(sentiment_dict.values())
        if total == 0:
            return 0.0
        return round(sentiment_dict.get(label, 0) / total, 4)
        
    metrics = [
        {
            "name": "Total Volume",
            "unit": "mentions"
        },
        {
            "name": "Average Rating",
            "unit": "stars"
        },
        {
            "name": "Positive Sentiment Ratio",
            "unit": "ratio"
        },
        {
            "name": "Negative Sentiment Ratio",
            "unit": "ratio"
        }
    ]
    
    for m in metrics:
        for b in brand_list:
            brand_data = overview.get(b, {})
            brand_sent = brand_data.get("sentiment", {})
            if m["name"] == "Total Volume":
                m[b] = brand_data.get("total_volume", 0)
            elif m["name"] == "Average Rating":
                m[b] = brand_data.get("avg_rating", 0.0)
            elif m["name"] == "Positive Sentiment Ratio":
                m[b] = calc_ratio(brand_sent, "positive")
            elif m["name"] == "Negative Sentiment Ratio":
                m[b] = calc_ratio(brand_sent, "negative")
                
    return {"metrics": metrics}

@router.get("/aspects")
def get_aspect_metrics(brand: Optional[str] = Query(None, description="Filter by brand"), db: Session = Depends(get_db)):
    logger.info(f"Retrieving aspect metrics: brand={brand}")
    
    query = db.query(
        AspectResult.brand,
        AspectResult.aspect,
        AspectResult.sentiment_label,
        func.count(AspectResult.id).label("count")
    )
    if brand:
        query = query.filter(AspectResult.brand == brand.lower())
        
    stats = query.group_by(
        AspectResult.brand, AspectResult.aspect, AspectResult.sentiment_label
    ).all()
    
    db_brands = [brand.lower()] if brand else get_all_brands(db)
    
    # Structure the response
    comparison = {}
    for aspect in ASPECTS:
        comparison[aspect] = {
            b: {"positive": 0, "neutral": 0, "negative": 0, "summary": "N/A"} for b in db_brands
        }
        
    for stat in stats:
        b = stat.brand.lower()
        asp = stat.aspect
        label = stat.sentiment_label
        if asp in comparison and b in db_brands:
            comparison[asp][b][label] = stat.count
            
    # Compute predominant sentiment for summary
    for asp in ASPECTS:
        for b in db_brands:
            brand_data = comparison[asp][b]
            pos = brand_data["positive"]
            neu = brand_data["neutral"]
            neg = brand_data["negative"]
            
            total = pos + neu + neg
            if total > 0:
                # Find label with max count
                max_val = max(pos, neu, neg)
                if max_val == pos:
                    brand_data["summary"] = "positive"
                elif max_val == neg:
                    brand_data["summary"] = "negative"
                else:
                    brand_data["summary"] = "neutral"
                    
    return comparison

@router.get("/topics")
def get_topic_metrics(brand: Optional[str] = Query(None, description="Filter by brand"), db: Session = Depends(get_db)):
    logger.info(f"Retrieving topic modeling metrics: brand={brand}")
    
    query = db.query(
        TopicResult.topic_name,
        TopicResult.brand,
        func.count(TopicResult.id).label("count")
    )
    if brand:
        query = query.filter(TopicResult.brand == brand.lower())
        
    counts = query.group_by(TopicResult.topic_name, TopicResult.brand).all()
    
    db_brands = [brand.lower()] if brand else get_all_brands(db)
    
    # Pivot counts by topic
    topics_dict = {}
    for row in counts:
        name = row.topic_name
        b = row.brand.lower()
        if name not in topics_dict:
            topics_dict[name] = {br: 0 for br in db_brands}
            topics_dict[name]["samples"] = []
        if b in db_brands:
            topics_dict[name][b] = row.count
            
    # For each topic, fetch up to 3 sample reviews from processed_mentions
    for name in topics_dict.keys():
        sample_query = db.query(
            ProcessedMention.cleaned_text,
            ProcessedMention.brand,
            ProcessedMention.sentiment_label
        ).join(
            TopicResult, ProcessedMention.id == TopicResult.source_id
        ).filter(
            TopicResult.topic_name == name
        )
        if brand:
            sample_query = sample_query.filter(TopicResult.brand == brand.lower())
            
        samples = sample_query.limit(3).all()
        
        topics_dict[name]["samples"] = [
            {
                "text": s.cleaned_text,
                "brand": s.brand,
                "sentiment": s.sentiment_label
            }
            for s in samples
        ]
        
    # Format as list of dicts for frontend convenience
    formatted = []
    for name, data in topics_dict.items():
        brand_counts = {b: data[b] for b in db_brands}
        formatted.append({
            "name": name,
            "samples": data["samples"],
            **brand_counts
        })
        
    # Sort topics by total volume (descending)
    formatted.sort(key=lambda x: sum(x[b] for b in db_brands), reverse=True)
    return formatted

@router.get("/search")
def search_reviews(
    q: str = Query(..., description="Search query string"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment"),
    source: Optional[str] = Query(None, description="Filter by source"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    logger.info(f"Elasticsearch search hit: query='{q}', brand={brand}, sentiment={sentiment}, source={source}")
    try:
        # Construct Elasticsearch bool query
        must_queries = [
            {
                "match": {
                    "cleaned_text": {
                        "query": q,
                        "fuzziness": "AUTO"
                    }
                }
            }
        ]
        
        filter_queries = []
        if brand and brand.lower() != "all":
            filter_queries.append({"term": {"brand": brand.lower()}})
        if sentiment and sentiment.lower() != "all":
            filter_queries.append({"term": {"sentiment_label": sentiment.lower()}})
        if source and source.lower() != "all":
            filter_queries.append({"term": {"source": source.lower()}})
            
        es_query = {
            "query": {
                "bool": {
                    "must": must_queries,
                    "filter": filter_queries
                }
            },
            "highlight": {
                "pre_tags": ["<em style='background-color: rgba(251, 188, 5, 0.25); color: #fbbc05; font-style: normal; font-weight: 600; padding: 0.05rem 0.2rem; border-radius: 4px;'>"],
                "post_tags": ["</em>"],
                "fields": {
                    "cleaned_text": {}
                }
            },
            "from": skip,
            "size": limit
        }
        
        # Execute query
        res = es.search(index=INDEX_NAME, body=es_query)
        hits = res["hits"]["hits"]
        total = res["hits"]["total"]["value"] if isinstance(res["hits"]["total"], dict) else res["hits"]["total"]
        
        results = []
        for hit in hits:
            source_doc = hit["_source"]
            highlight = hit.get("highlight", {}).get("cleaned_text", [])
            highlight_snippet = highlight[0] if highlight else source_doc["cleaned_text"]
            
            results.append({
                "id": source_doc["mention_id"],
                "brand": source_doc["brand"],
                "source": source_doc["source"],
                "author": source_doc["author"],
                "post_date": source_doc["post_date"],
                "cleaned_text": source_doc["cleaned_text"],
                "sentiment_label": source_doc["sentiment_label"],
                "sentiment_score": source_doc["sentiment_score"],
                "highlight": highlight_snippet,
                "score": hit["_score"]
            })
            
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": results
        }
        
    except Exception as e:
        logger.error(f"Elasticsearch search failed: {e}")
        # Fallback empty list if ES index is not found/initialized yet
        return {
            "total": 0,
            "skip": skip,
            "limit": limit,
            "items": [],
            "error": str(e)
        }

@router.get("/alerts")
def get_recent_alerts(brand: Optional[str] = Query(None, description="Filter by brand"), db: Session = Depends(get_db)):
    from app.db.models.alert_log import AlertLog
    try:
        query = db.query(AlertLog)
        if brand:
            query = query.filter(AlertLog.brand == brand.lower())
        alerts = query.order_by(AlertLog.timestamp.desc()).limit(50).all()
        
        return {
            "status": "success",
            "alerts": [
                {
                    "id": a.id,
                    "alert_type": a.alert_type,
                    "brand": a.brand,
                    "severity": a.severity,
                    "message": a.message,
                    "timestamp": a.timestamp.isoformat() if a.timestamp else None
                } for a in alerts
            ]
        }
    except Exception as e:
        logger.error(f"Failed to fetch alerts: {e}")
        return {"status": "error", "message": str(e), "alerts": []}

class AlertSendRequest(BaseModel):
    emails: List[str]

@router.post("/alerts/send")
def send_alert_emails(request: AlertSendRequest, db: Session = Depends(get_db)):
    from app.db.models.alert_log import AlertLog
    from app.utils.pdf_generator import get_brand_health_analysis, get_recent_news, generate_weekly_pdf_report
    from email.mime.application import MIMEApplication
    
    try:
        # 1. Fetch latest system alerts
        alerts = db.query(AlertLog).order_by(AlertLog.timestamp.desc()).limit(10).all()
        
        # 2. Fetch Brand Health Summary (Currently Working Analysis)
        brand_data = get_brand_health_analysis(db)
        
        # 3. Fetch Recent Customer Voice / News
        recent_news = get_recent_news(db, limit=3)
        
        # 4. Generate the PDF Report on the fly
        pdf_path, _ = generate_weekly_pdf_report(db)
        
        # 5. Build System Alert HTML list
        alerts_html = ""
        for a in alerts:
            color = "#ba1a1a" if a.severity.lower() == "high" else ("#d97706" if a.severity.lower() == "medium" else "#006c49")
            brand_upper = a.brand.upper() if a.brand else "UNKNOWN"
            alert_type_fmt = a.alert_type.replace('_', ' ').title() if a.alert_type else "Alert"
            timestamp_str = a.timestamp.strftime('%Y-%m-%d %H:%M:%S') if a.timestamp else 'N/A'
            alerts_html += f"""
            <div style="margin-bottom: 12px; padding: 12px 15px; border-left: 4px solid {color}; background-color: #f9fafb; border-radius: 6px; border: 1px solid #e2e8f0; border-left-width: 4px;">
                <h4 style="margin: 0 0 4px 0; color: #111827; font-size: 14px;">[{brand_upper}] {alert_type_fmt}</h4>
                <p style="margin: 0; color: #4b5563; font-size: 13px; line-height: 1.4;">{a.message}</p>
                <small style="color: #9ca3af; display: block; margin-top: 6px; font-size: 11px;">Severity: <strong>{a.severity}</strong> | Time: {timestamp_str}</small>
            </div>
            """
            
        if not alerts:
            alerts_html = """
            <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
                <div style="color: #166534; font-weight: 600; font-size: 14px; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
                    <span style="font-size: 16px; display: inline-block;">✔️</span> System Status: Stable
                </div>
                <p style="margin: 0; color: #4b5563; font-size: 13px; line-height: 1.45;">
                    No high-severity sentiment spikes or critical topic surges were triggered today. All monitored brands are operating within normal baseline parameters.
                </p>
            </div>
            """

        # 6. Build Brand Health Standings Table
        brand_rows_html = ""
        for b_name, b_info in brand_data.items():
            bg_color = "#f8fafc" if b_name in ["amazon", "meesho"] else "#ffffff"
            brand_rows_html += f"""
            <tr style="background-color: {bg_color};">
                <td style="padding: 10px 12px; font-weight: bold; font-size: 13px; border-bottom: 1px solid #e2e8f0; color: #1f2937;">{b_name.capitalize()}</td>
                <td style="padding: 10px 12px; text-align: center; font-size: 13px; border-bottom: 1px solid #e2e8f0; color: #4b5563;">{b_info['volume']:,}</td>
                <td style="padding: 10px 12px; text-align: center; font-size: 13px; border-bottom: 1px solid #e2e8f0; color: #f59e0b; font-weight: bold;">{b_info['rating']} ★</td>
                <td style="padding: 10px 12px; text-align: center; font-size: 13px; border-bottom: 1px solid #e2e8f0; color: #166534; font-weight: bold;">{b_info['pos_ratio']}%</td>
                <td style="padding: 10px 12px; text-align: center; font-size: 13px; border-bottom: 1px solid #e2e8f0; color: #991b1b; font-weight: bold;">{b_info['neg_ratio']}%</td>
            </tr>
            """

        # 7. Build Recent News list
        news_html = ""
        for n in recent_news:
            sentiment_color = "#15803d" if n['sentiment'] == 'positive' else ("#b91c1c" if n['sentiment'] == 'negative' else "#4b5563")
            news_html += f"""
            <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                <div style="display: flex; justify-content: space-between; font-size: 11px; color: #6b7280; font-weight: bold; margin-bottom: 6px;">
                    <span style="color: #006c49; text-transform: uppercase;">[{n['brand'].upper()}] via {n['source'].capitalize()}</span>
                    <span style="color: {sentiment_color}; font-weight: bold; text-transform: uppercase;">{n['sentiment']}</span>
                </div>
                <p style="margin: 0; font-size: 13px; color: #374151; font-style: italic; line-height: 1.45;">"{n['text']}"</p>
                <div style="text-align: right; margin-top: 4px; font-size: 10px; color: #9ca3af;">{n['date']}</div>
            </div>
            """
        if not recent_news:
            news_html = "<p style='color: #6b7280; font-size: 13px;'>No recent mentions processed in the database.</p>"

        # 8. Complete Gorgeous Email Template
        html_content = f"""
        <html>
            <body style="font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; line-height: 1.6; color: #374151; background-color: #f4f6f8; margin: 0; padding: 20px;">
                <table cellpadding="0" cellspacing="0" width="100%" style="max-width: 650px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #006c49 0%, #004b33 100%); padding: 30px 25px; text-align: center; color: #ffffff;">
                            <h1 style="margin: 0; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">SocialIntel AI Platform</h1>
                            <p style="margin: 6px 0 0 0; font-size: 13px; color: #a7f3d0; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600;">Executive Intelligence & Alerts</p>
                        </td>
                    </tr>
                    <!-- Main Body -->
                    <tr>
                        <td style="padding: 25px;">
                            <p style="margin-top: 0; font-size: 15px; color: #1f2937;">Hello,</p>
                            <p style="font-size: 14px; color: #4b5563; margin-bottom: 25px;">
                                Your weekly intelligence summary and brand analysis report are ready. We have attached the full <strong>Weekly Social Intelligence Report (PDF)</strong> containing comprehensive metrics and deep analytical breakdowns.
                            </p>

                            <!-- SECTION A: System Alerts -->
                            <h3 style="color: #006c49; font-size: 16px; margin: 25px 0 12px 0; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; font-weight: bold; display: flex; align-items: center; gap: 6px;">
                                <span style="font-size: 18px;">🔔</span> Critical Intelligence Alerts
                            </h3>
                            <div style="margin-bottom: 25px;">
                                {alerts_html}
                            </div>

                            <!-- SECTION B: Currently Working Analysis (Standings) -->
                            <h3 style="color: #006c49; font-size: 16px; margin: 25px 0 12px 0; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; font-weight: bold; display: flex; align-items: center; gap: 6px;">
                                <span style="font-size: 18px;">📊</span> Brand Health Standings (Current Status)
                            </h3>
                            <table style="width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px;">
                                <thead>
                                    <tr style="background-color: #f1f5f9; color: #475569; font-weight: bold;">
                                        <th style="padding: 10px 12px; text-align: left; font-size: 12px; border-bottom: 2px solid #e2e8f0; text-transform: uppercase; letter-spacing: 0.5px;">Brand</th>
                                        <th style="padding: 10px 12px; text-align: center; font-size: 12px; border-bottom: 2px solid #e2e8f0; text-transform: uppercase; letter-spacing: 0.5px;">Mentions</th>
                                        <th style="padding: 10px 12px; text-align: center; font-size: 12px; border-bottom: 2px solid #e2e8f0; text-transform: uppercase; letter-spacing: 0.5px;">Avg Rating</th>
                                        <th style="padding: 10px 12px; text-align: center; font-size: 12px; border-bottom: 2px solid #e2e8f0; text-transform: uppercase; letter-spacing: 0.5px;">Positive</th>
                                        <th style="padding: 10px 12px; text-align: center; font-size: 12px; border-bottom: 2px solid #e2e8f0; text-transform: uppercase; letter-spacing: 0.5px;">Negative</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {brand_rows_html}
                                </tbody>
                            </table>

                            <!-- SECTION C: Today's Recent News -->
                            <h3 style="color: #006c49; font-size: 16px; margin: 25px 0 12px 0; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; font-weight: bold; display: flex; align-items: center; gap: 6px;">
                                <span style="font-size: 18px;">📰</span> Today's Recent Feedback & News
                            </h3>
                            <div style="margin-bottom: 25px;">
                                {news_html}
                            </div>

                            <!-- Call to Action -->
                            <div style="text-align: center; margin-top: 30px; margin-bottom: 20px;">
                                <a href="http://localhost:5173" style="background-color: #006c49; color: #ffffff; text-decoration: none; padding: 12px 28px; border-radius: 25px; font-size: 14px; font-weight: bold; display: inline-block; box-shadow: 0 4px 6px rgba(0,108,73,0.15); transition: background-color 0.2s;">
                                    Access SocialIntel Dashboard
                                </a>
                            </div>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8fafc; padding: 20px 25px; border-top: 1px solid #e2e8f0; text-align: center; font-size: 12px; color: #94a3b8;">
                            <p style="margin: 0 0 5px 0; font-weight: bold; color: #64748b;">Generated securely by SocialIntel AI Platform</p>
                            <p style="margin: 0;">This email contains sensitive market insights. Do not forward. Please do not reply directly to this message.</p>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """

        # Check SMTP configuration
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.error("SMTP_USER or SMTP_PASSWORD not set")
            return {"status": "error", "message": "SMTP credentials not configured in backend"}
            
        # 9. Create email message
        msg = MIMEMultipart("mixed")  # Use mixed to allow attachments and body
        msg["Subject"] = "SocialIntel Weekly Analysis & Brand Status Report"
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
        msg["To"] = ", ".join(request.emails)
        
        # Attach HTML content
        msg_body = MIMEMultipart("alternative")
        msg_body.attach(MIMEText(html_content, "html"))
        msg.attach(msg_body)
        
        # Attach PDF Report
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                pdf_part = MIMEApplication(f.read(), Name=os.path.basename(pdf_path))
            pdf_part['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
            msg.attach(pdf_part)
            logger.info(f"Attached PDF report {pdf_path} to email.")
        else:
            logger.error(f"Generated PDF file not found at {pdf_path}, skipping attachment.")
        
        # Send email
        logger.info(f"Connecting to SMTP server {settings.SMTP_SERVER}:{settings.SMTP_PORT}")
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, request.emails, msg.as_string())
        server.quit()
        logger.info(f"Emails sent successfully to {request.emails}")

        return {"status": "success", "message": f"Alert email with PDF report sent successfully to {len(request.emails)} recipients."}

    except Exception as e:
        logger.error(f"Failed to send email alerts: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/competitor-analysis")
def get_competitor_analysis(brands: str, db: Session = Depends(get_db)):
    """
    Compare multiple brands: e.g. /competitor-analysis?brands=amazon,flipkart
    """
    brand_list = [b.strip().lower() for b in brands.split(",")]
    
    results = {}
    for b in brand_list:
        mentions = db.query(ProcessedMention).filter(ProcessedMention.brand == b).all()
        total = len(mentions)
        neg_count = sum(1 for m in mentions if m.sentiment_label == "negative")
        neg_ratio = (neg_count / total * 100) if total > 0 else 0
        
        pos_count = sum(1 for m in mentions if m.sentiment_label == "positive")
        pos_ratio = (pos_count / total * 100) if total > 0 else 0
        score = pos_ratio - neg_ratio
        
        results[b] = {
            "total_mentions": total,
            "negative_ratio": round(neg_ratio, 2),
            "positive_ratio": round(pos_ratio, 2),
            "net_sentiment_score": round(score, 2)
        }
        
    return {"status": "success", "comparison": results}

@router.get("/insights")
def get_executive_insights(brand: Optional[str] = Query(None, description="Filter by brand"), db: Session = Depends(get_db)):
    from app.db.models.executive_insight import ExecutiveInsight
    # Fetch latest 1 per brand
    query = db.query(ExecutiveInsight)
    if brand:
        query = query.filter(ExecutiveInsight.brand == brand.lower())
    insights = query.order_by(ExecutiveInsight.generated_at.desc()).limit(20).all()
    latest_insights = {}
    for i in insights:
        if i.brand not in latest_insights:
            latest_insights[i.brand] = {
                "id": i.id,
                "brand": i.brand,
                "top_risk": i.top_risk,
                "top_opportunity": i.top_opportunity_summary or i.top_opportunity,
                "executive_summary": i.executive_summary,
                "generated_at": i.generated_at.isoformat() if i.generated_at else None
            }
    
    return {"status": "success", "insights": list(latest_insights.values())}

@router.get("/reports")
def get_reports(db: Session = Depends(get_db)):
    from app.db.models.generated_report import GeneratedReport
    reports = db.query(GeneratedReport).order_by(GeneratedReport.generated_at.desc()).limit(10).all()
    
    return {"status": "success", "reports": [
        {
            "id": r.id,
            "report_type": r.report_type,
            "summary": r.summary,
            "generated_at": r.generated_at.isoformat() if r.generated_at else None
        } for r in reports
    ]}

from fastapi.responses import FileResponse
import os

@router.get("/reports/download/{report_id}")
def download_report(report_id: int, db: Session = Depends(get_db)):
    from app.db.models.generated_report import GeneratedReport
    from fastapi import HTTPException
    
    report = db.query(GeneratedReport).filter(GeneratedReport.id == report_id).first()
    if not report or not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Report not found")
        
    return FileResponse(path=report.file_path, filename=os.path.basename(report.file_path), media_type='application/pdf')

@router.get("/rankings")
def get_rankings(db: Session = Depends(get_db)):
    """
    Calculate and return a ranked list of brands based on the Unified Ranking Algorithm.
    Formula: (Net Sentiment Score * 0.6) + (Normalized Volume * 0.2) + (Normalized Engagement * 0.2) = Final Rank Score
    """
    brands = db.query(ProcessedMention.brand).distinct().all()
    brand_list = [b[0] for b in brands if b[0]]
    
    raw_metrics = {}
    max_volume = 0
    max_engagement = 0
    
    for b in brand_list:
        mentions = db.query(ProcessedMention).filter(ProcessedMention.brand == b).all()
        volume = len(mentions)
        engagement = sum((m.engagement_score or 0) for m in mentions)
        
        neg_count = sum(1 for m in mentions if m.sentiment_label == "negative")
        neg_ratio = (neg_count / volume * 100) if volume > 0 else 0
        
        pos_count = sum(1 for m in mentions if m.sentiment_label == "positive")
        pos_ratio = (pos_count / volume * 100) if volume > 0 else 0
        net_sentiment = pos_ratio - neg_ratio
        
        raw_metrics[b] = {
            "volume": volume,
            "engagement": engagement,
            "net_sentiment": net_sentiment
        }
        
        if volume > max_volume:
            max_volume = volume
        if engagement > max_engagement:
            max_engagement = engagement
            
    # Calculate final scores
    rankings = []
    for b, metrics in raw_metrics.items():
        norm_volume = (metrics["volume"] / max_volume * 100) if max_volume > 0 else 0
        norm_engagement = (metrics["engagement"] / max_engagement * 100) if max_engagement > 0 else 0
        
        final_score = (metrics["net_sentiment"] * 0.6) + (norm_volume * 0.2) + (norm_engagement * 0.2)
        
        rankings.append({
            "brand": b.capitalize(),
            "final_score": round(final_score, 2),
            "net_sentiment": round(metrics["net_sentiment"], 2),
            "volume": metrics["volume"],
            "engagement": metrics["engagement"]
        })
        
    # Sort by final_score descending
    rankings.sort(key=lambda x: x["final_score"], reverse=True)
    
    # Assign ranks
    for i, item in enumerate(rankings):
        item["rank"] = i + 1
        
    return {"status": "success", "rankings": rankings}


class ChatMessage(BaseModel):
    role: str  # 'user' or 'model'
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []


@router.post("/chat")
def chat_with_assistant(request: ChatRequest, db: Session = Depends(get_db)):
    import os
    import json
    from google import genai
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    # 1. Base navigation intent fallback parsing
    msg = request.message.lower()
    navigate_to = None
    if "compare" in msg or "comparison" in msg:
        brands_found = []
        for b in ["amazon", "flipkart", "meesho", "myntra"]:
            if b in msg:
                brands_found.append(b)
        if brands_found:
            navigate_to = f"/compare?brands={','.join(brands_found)}"
        else:
            navigate_to = "/compare"
    elif "alert" in msg:
        navigate_to = "/alerts"
    elif "report" in msg:
        navigate_to = "/reports"
    elif "insight" in msg or "executive" in msg or "intelligence" in msg:
        navigate_to = "/intelligence"
    elif "search" in msg:
        if "search for" in msg:
            query_part = msg.split("search for")[-1].strip().replace(" ", "+")
            navigate_to = f"/search?q={query_part}"
        else:
            navigate_to = "/search"
    elif "overview" in msg or "dashboard" in msg or "home" in msg:
        navigate_to = "/"
    else:
        for b in ["amazon", "flipkart", "meesho", "myntra"]:
            if b in msg:
                navigate_to = f"/brands/{b}"
                break

    if not api_key or "your_gemini" in api_key.lower():
        # Fallback response
        if navigate_to == "/":
            ans = "Returning to the Dashboard Overview."
        elif navigate_to and navigate_to.startswith("/brands/"):
            brand_name = navigate_to.split("/")[-1]
            ans = f"Taking you to the details page for {brand_name.capitalize()}."
        elif navigate_to == "/compare":
            ans = "Taking you to the Competitor Analysis page."
        elif navigate_to and navigate_to.startswith("/compare?brands="):
            ans = "Opening the comparison view for the selected brands."
        elif navigate_to == "/alerts":
            ans = "Navigating you to the Alerts page to view system warnings and anomalies."
        elif navigate_to == "/reports":
            ans = "Taking you to the Reports page where you can manage and generate PDF summaries."
        elif navigate_to and navigate_to.startswith("/search"):
            ans = "Opening Search Intelligence to filter reviews."
        elif navigate_to == "/intelligence":
            ans = "Opening the Executive Intelligence page."
        else:
            ans = "I am a helpful assistant. You can ask me to compare brands, search reviews, show alerts/reports, or navigate the dashboard!"
        logger.info("Chatbot running in offline/fallback mode due to missing or invalid GEMINI_API_KEY")
        return {
            "answer": ans,
            "navigate_to": navigate_to
        }
        
    try:
        # 2. Fetch real-time system context for RAG
        overview_data = get_overview(db)
        
        from app.db.models.alert_log import AlertLog
        alerts = db.query(AlertLog).order_by(AlertLog.timestamp.desc()).limit(15).all()
        alerts_list = [
            {
                "brand": a.brand,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "timestamp": a.timestamp.isoformat() if a.timestamp else None
            }
            for a in alerts
        ]
        
        from app.db.models.executive_insight import ExecutiveInsight
        insights = db.query(ExecutiveInsight).order_by(ExecutiveInsight.generated_at.desc()).limit(15).all()
        insights_list = [
            {
                "brand": i.brand,
                "top_risk": i.top_risk,
                "top_opportunity": i.top_opportunity_summary or i.top_opportunity,
                "executive_summary": i.executive_summary
            }
            for i in insights
        ]
        
        context = {
            "brands_overview": overview_data,
            "recent_alerts": alerts_list,
            "executive_insights": insights_list
        }
        
        # 3. Build system instructions
        system_instruction = """You are a helpful and intelligent AI Chatbot for the Social Product Intelligence platform (named SocialIntel).
Your goal is to answer the user's questions about the project's data (brands, sentiment, reviews, alerts, reports) using the provided real-time system context, and to suggest navigation actions where appropriate.

Rules:
1. Use the provided "System Context" to answer questions about the brands, metrics, alerts, and reports. If the user asks a question like "How is Amazon doing?", summarize its metrics, average rating, sentiment, and mention its top risks/opportunities.
2. If the user's query indicates an intent to view or navigate to a specific page or report, you MUST provide the correct route path in the `navigate_to` field of the JSON response.
Here are the mapping rules for `navigate_to`:
- Dashboard Overview: `/` (Suggested if the user asks to see the overview, dashboard, home page, or general status)
- Specific Brand Details: `/brands/<brand_name>` (Suggested if the user asks about a specific brand like Amazon, Flipkart, Meesho, or Myntra, e.g., "Show me Amazon's details" or "Take me to Flipkart page")
- Competitor Analysis / Comparison: `/compare` (Suggested if the user wants to compare brands. If they mention specific brands to compare, append them as query parameters, e.g., `/compare?brands=amazon,flipkart` or `/compare?brands=meesho,myntra`)
- Alerts: `/alerts` (Suggested if the user wants to see alerts, notifications, anomalies, or system warnings)
- Reports: `/reports` (Suggested if the user wants to see reports, PDFs, or download documents)
- Search: `/search` (Suggested if the user wants to search reviews. If they specify a query, e.g., "search for packaging issue", use `/search?q=packaging+issue`. If they just say "take me to search", use `/search`)
- Executive Intelligence: `/intelligence` (Suggested if the user asks for executive insights, opportunities/risks summaries, or AI summaries)
- If there is no navigation intent or the user is just chatting, set `navigate_to` to null.

You must return a JSON response with two fields:
{
  "answer": "A markdown-formatted, user-friendly response text answering the user's query utilizing the context when relevant. Do not mention that you got it from a 'JSON context block' or 'provided system data'; talk as if you are directly integrated with the system.",
  "navigate_to": "..." // string route or null
}"""

        # 4. Format chat history
        history_str = ""
        for h in request.history:
            sender = "User" if h.role == "user" else "Assistant"
            history_str += f"{sender}: {h.content}\n"
            
        prompt = f"""System Context:
{json.dumps(context, indent=2)}

Chat History:
{history_str}
User: {request.message}
Assistant:"""
        
        # 5. Call Gemini
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'system_instruction': system_instruction
            }
        )
        
        resp_text = response.text.strip()
        result = json.loads(resp_text)
        return result
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return {
            "answer": f"Sorry, I encountered an error while processing your request: {str(e)}",
            "navigate_to": navigate_to
        }

