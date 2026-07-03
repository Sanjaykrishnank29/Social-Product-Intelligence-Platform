from sqlalchemy import Column, BigInteger, Text, Float, DateTime, ForeignKey, Integer
from app.db.session import Base

class RawMention(Base):
    __tablename__ = "raw_mentions"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    brand = Column(Text, nullable=False, index=True)
    source = Column(Text, nullable=False, index=True)
    external_id = Column(Text, unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    rating = Column(Float, nullable=True)
    author = Column(Text, nullable=True)
    post_date = Column(DateTime(timezone=True), nullable=True)
    engagement_score = Column(Integer, nullable=True, default=0)

class ProcessedMention(Base):
    __tablename__ = "processed_mentions"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    source_id = Column(BigInteger, ForeignKey("raw_mentions.id", ondelete="CASCADE"), nullable=False, index=True)
    brand = Column(Text, nullable=False, index=True)
    source = Column(Text, nullable=False, index=True)
    author = Column(Text, nullable=True)
    post_date = Column(DateTime(timezone=True), nullable=True)
    cleaned_text = Column(Text, nullable=False)
    language = Column(Text, nullable=True)
    sentiment_label = Column(Text, nullable=True, index=True)
    sentiment_score = Column(Float, nullable=True)
    engagement_score = Column(Integer, nullable=True, default=0)

class AspectResult(Base):
    __tablename__ = "aspect_results"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    source_id = Column(BigInteger, ForeignKey("processed_mentions.id", ondelete="CASCADE"), nullable=False, index=True)
    brand = Column(Text, nullable=False, index=True)
    aspect = Column(Text, nullable=False, index=True)
    sentiment_label = Column(Text, nullable=False, index=True)
    sentiment_score = Column(Float, nullable=False)

class TopicResult(Base):
    __tablename__ = "topic_results"

    id = Column(BigInteger, primary_key=True, autoincrement=True, index=True)
    source_id = Column(BigInteger, ForeignKey("processed_mentions.id", ondelete="CASCADE"), nullable=False, index=True)
    brand = Column(Text, nullable=False, index=True)
    topic_id = Column(Integer, nullable=False, index=True)
    topic_name = Column(Text, nullable=False)






