from sqlalchemy import Column, BigInteger, Text, DateTime, JSON
from datetime import datetime, timezone
from app.db.session import Base

class ExecutiveInsight(Base):
    __tablename__ = "executive_insights"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    brand = Column(Text, nullable=False, index=True)
    top_risk = Column(Text, nullable=True)
    top_opportunity = Column(Text, nullable=True)  # Legacy
    top_opportunity_summary = Column(Text, nullable=True)
    top_opportunity_json = Column(JSON, nullable=True)
    executive_summary = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
