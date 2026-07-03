from sqlalchemy import Column, BigInteger, Text, DateTime
from datetime import datetime, timezone
from app.db.session import Base

class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    report_type = Column(Text, nullable=False, index=True) # e.g. 'weekly_intelligence'
    file_path = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    generated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
