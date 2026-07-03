from sqlalchemy import Column, BigInteger, Text, DateTime, Float, ForeignKey, Integer
from datetime import datetime, timezone
from app.db.session import Base

class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    stage_name = Column(Text, nullable=False, index=True)
    status = Column(Text, nullable=False, index=True) # pending, success, failed
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
