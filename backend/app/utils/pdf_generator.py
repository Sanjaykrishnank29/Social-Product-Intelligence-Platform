import os
import logging
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from app.db.models.executive_insight import ExecutiveInsight
from app.db.models.generated_report import GeneratedReport
from app.db.models.mention import ProcessedMention, RawMention
from sqlalchemy import func
from sqlalchemy.orm import Session

logger = logging.getLogger("pdf_generator")

def get_brand_health_analysis(db: Session):
    brands = ["amazon", "flipkart", "meesho", "myntra"]
    results = {}
    for b in brands:
        # Volume
        volume = db.query(RawMention).filter(RawMention.brand == b).count()
        # Avg Rating
        avg_rating_res = db.query(func.avg(RawMention.rating)).filter(RawMention.brand == b).scalar()
        avg_rating = round(float(avg_rating_res or 0), 1)
        
        # Sentiment
        pos_count = db.query(ProcessedMention).filter(ProcessedMention.brand == b, ProcessedMention.sentiment_label == "positive").count()
        neg_count = db.query(ProcessedMention).filter(ProcessedMention.brand == b, ProcessedMention.sentiment_label == "negative").count()
        total_sent = db.query(ProcessedMention).filter(ProcessedMention.brand == b).count()
        
        pos_ratio = (pos_count / total_sent * 100) if total_sent > 0 else 0.0
        neg_ratio = (neg_count / total_sent * 100) if total_sent > 0 else 0.0
        
        # Latest insight
        insight = db.query(ExecutiveInsight).filter(ExecutiveInsight.brand == b).order_by(ExecutiveInsight.generated_at.desc()).first()
        
        results[b] = {
            "volume": volume,
            "rating": avg_rating,
            "pos_ratio": round(pos_ratio, 1),
            "neg_ratio": round(neg_ratio, 1),
            "executive_summary": insight.executive_summary if insight else "No brand analysis summary available yet.",
            "top_risk": insight.top_risk if insight else "No critical risks identified.",
            "top_opportunity": (insight.top_opportunity_summary or insight.top_opportunity) if insight else "No opportunities identified yet."
        }
    return results

def get_recent_news(db: Session, limit=5):
    # Fetch latest processed mentions
    mentions = db.query(ProcessedMention).order_by(ProcessedMention.post_date.desc()).limit(limit).all()
    news = []
    for m in mentions:
        news.append({
            "brand": m.brand,
            "source": m.source,
            "author": m.author,
            "date": m.post_date.strftime("%Y-%m-%d") if m.post_date else "N/A",
            "sentiment": m.sentiment_label,
            "text": m.cleaned_text
        })
    return news

def generate_weekly_pdf_report(db: Session, custom_file_path: str = None) -> tuple[str, GeneratedReport]:
    logger.info("Generating Weekly Report PDF...")
    
    # 1. Fetch data
    brand_data = get_brand_health_analysis(db)
    recent_news = get_recent_news(db, limit=5)
    
    # 2. Determine file path
    if custom_file_path:
        file_path = custom_file_path
    else:
        # Base dir is backend/
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        host_pdf_dir = os.path.abspath(os.path.join(base_dir, "../generated_pdfs"))
        
        # Fallback to local app/generated_pdfs if root-level is not accessible (e.g. in container without mount)
        if os.path.exists(os.path.dirname(host_pdf_dir)):
            reports_dir = host_pdf_dir
        else:
            reports_dir = os.path.join(base_dir, "generated_pdfs")
            
        os.makedirs(reports_dir, exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"Weekly_Intelligence_Report_{timestamp_str}.pdf"
        file_path = os.path.join(reports_dir, file_name)
    
    # 3. Setup document
    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles to look gorgeous and clean
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#006c49'),
        alignment=1, # Center
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#5f6368'),
        alignment=1,
        spaceAfter=25
    )
    
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#006c49'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1f2937'),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6
    )
    
    header_cell_style = ParagraphStyle(
        'HeaderCell',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=1 # Center
    )
    
    cell_style = ParagraphStyle(
        'Cell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#1f2937')
    )
    
    cell_center_style = ParagraphStyle(
        'CellCenter',
        parent=cell_style,
        alignment=1
    )

    bold_cell_style = ParagraphStyle(
        'BoldCell',
        parent=cell_style,
        fontName='Helvetica-Bold'
    )
    
    story = []
    
    # Title & Metadata
    story.append(Paragraph("Weekly Social Intelligence & Analysis Report", title_style))
    current_date_str = datetime.now().strftime("%B %d, %Y")
    story.append(Paragraph(f"Generated on {current_date_str} | SocialIntel Analytics Platform", subtitle_style))
    story.append(Spacer(1, 10))
    
    # SECTION 1: Brand Health & Sentiment Analysis (Currently Working Status)
    story.append(Paragraph("1. Brand Health & Sentiment Analysis (Currently Working)", h1_style))
    story.append(Paragraph("Summary of overall consumer feedback volume, ratings, and sentiment ratios across all monitored platforms:", body_style))
    story.append(Spacer(1, 6))
    
    # Brand table data
    table_data = [
        [
            Paragraph("Brand", header_cell_style),
            Paragraph("Total Mentions", header_cell_style),
            Paragraph("Avg Rating", header_cell_style),
            Paragraph("Positive Ratio", header_cell_style),
            Paragraph("Negative Ratio", header_cell_style)
        ]
    ]
    
    for b, data in brand_data.items():
        table_data.append([
            Paragraph(b.capitalize(), bold_cell_style),
            Paragraph(f"{data['volume']:,}", cell_center_style),
            Paragraph(f"{data['rating']} / 5.0", cell_center_style),
            Paragraph(f"{data['pos_ratio']}%", cell_center_style),
            Paragraph(f"{data['neg_ratio']}%", cell_center_style)
        ])
        
    t_summary = Table(table_data, colWidths=[110, 105, 105, 110, 110])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#006c49')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 15))
    
    # SECTION 2: Detailed Executive Insights
    story.append(Paragraph("2. Brand Executive Insights", h1_style))
    
    for b, data in brand_data.items():
        story.append(Paragraph(f"{b.capitalize()}", h2_style))
        story.append(Paragraph(f"<b>Executive Summary:</b> {data['executive_summary']}", body_style))
        
        insight_data = [
            [Paragraph("<b>Top Risk</b>", cell_style), Paragraph(data['top_risk'], cell_style)],
            [Paragraph("<b>Top Opportunity</b>", cell_style), Paragraph(data['top_opportunity'], cell_style)]
        ]
        t_insight = Table(insight_data, colWidths=[110, 430])
        t_insight.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), colors.HexColor('#fef2f2')),
            ('BACKGROUND', (0,1), (0,1), colors.HexColor('#f0fdf4')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_insight)
        story.append(Spacer(1, 10))
        
    story.append(PageBreak()) # Clean page break for recent news
    
    # SECTION 3: Today's Recent News & Customer Feedback
    story.append(Paragraph("3. Recent News & Customer Feedback", h1_style))
    story.append(Paragraph("Below is a sample of recent brand mentions, customer feedback, and news items currently being analyzed by the platform:", body_style))
    story.append(Spacer(1, 8))
    
    if not recent_news:
        story.append(Paragraph("No recent news or customer feedback processed in the database yet.", body_style))
    else:
        for idx, news_item in enumerate(recent_news):
            sentiment_color = "#15803d" if news_item['sentiment'] == 'positive' else ("#b91c1c" if news_item['sentiment'] == 'negative' else "#4b5563")
            sentiment_badge = f"<font color='{sentiment_color}'><b>{news_item['sentiment'].upper()}</b></font>"
            
            header_text = f"<b>#{idx+1} [{news_item['brand'].upper()}]</b> via {news_item['source'].capitalize()} | Sentiment: {sentiment_badge} | Date: {news_item['date']}"
            story.append(Paragraph(header_text, h2_style))
            story.append(Paragraph(f"\"{news_item['text']}\"", body_style))
            story.append(Spacer(1, 8))
            
    # Build the document
    doc.build(story)
    
    # Save GeneratedReport record in DB
    summary_text = f"Weekly intelligence report for {len(brand_data)} brands including today recent news and working analytics."
    report = GeneratedReport(
        report_type="weekly_intelligence",
        file_path=file_path,
        summary=summary_text,
        generated_at=datetime.now(timezone.utc)
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    logger.info(f"Report generated successfully: {file_path}")
    return file_path, report
