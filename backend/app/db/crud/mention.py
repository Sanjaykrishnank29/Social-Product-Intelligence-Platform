from sqlalchemy.orm import Session
from app.db.models.mention import RawMention
from app.db.schemas.mention import RawMentionCreate
from typing import List, Optional

def get_raw_mention(db: Session, mention_id: int) -> Optional[RawMention]:
    return db.query(RawMention).filter(RawMention.id == mention_id).first()

def get_raw_mention_by_external_id(db: Session, external_id: str) -> Optional[RawMention]:
    return db.query(RawMention).filter(RawMention.external_id == external_id).first()

def get_raw_mentions(db: Session, skip: int = 0, limit: int = 100) -> List[RawMention]:
    return db.query(RawMention).offset(skip).limit(limit).all()

def create_raw_mention(db: Session, raw_mention: RawMentionCreate) -> RawMention:
    db_raw_mention = RawMention(
        brand=raw_mention.brand,
        source=raw_mention.source,
        external_id=raw_mention.external_id,
        content=raw_mention.content,
        rating=raw_mention.rating,
        author=raw_mention.author,
        post_date=raw_mention.post_date,
    )
    db.add(db_raw_mention)
    db.commit()
    db.refresh(db_raw_mention)
    return db_raw_mention

from app.db.models.mention import ProcessedMention
from app.db.schemas.mention import ProcessedMentionCreate

def get_processed_mention_by_cleaned_text(db: Session, cleaned_text: str, brand: str) -> Optional[ProcessedMention]:
    return db.query(ProcessedMention).filter(
        ProcessedMention.cleaned_text == cleaned_text,
        ProcessedMention.brand == brand
    ).first()

def get_processed_mentions(db: Session, skip: int = 0, limit: int = 100) -> List[ProcessedMention]:
    return db.query(ProcessedMention).offset(skip).limit(limit).all()

def create_processed_mention(db: Session, processed_mention: ProcessedMentionCreate) -> ProcessedMention:
    db_processed_mention = ProcessedMention(
        source_id=processed_mention.source_id,
        brand=processed_mention.brand,
        source=processed_mention.source,
        author=processed_mention.author,
        post_date=processed_mention.post_date,
        cleaned_text=processed_mention.cleaned_text,
        language=processed_mention.language,
        sentiment_label=processed_mention.sentiment_label,
        sentiment_score=processed_mention.sentiment_score,
    )
    db.add(db_processed_mention)
    db.commit()
    db.refresh(db_processed_mention)
    return db_processed_mention



