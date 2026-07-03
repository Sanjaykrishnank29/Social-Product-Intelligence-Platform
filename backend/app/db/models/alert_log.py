from sqlalchemy import Column, BigInteger, Text, DateTime
from datetime import datetime, timezone
from app.db.session import Base

class AlertLog(Base):
    __tablename__ = "alerts_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    alert_type = Column(Text, nullable=False, index=True) # sentiment_spike, topic_surge
    brand = Column(Text, nullable=False, index=True)
    severity = Column(Text, nullable=False) # e.g. High, Medium
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
