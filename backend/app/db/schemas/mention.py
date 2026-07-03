from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RawMentionBase(BaseModel):
    brand: str
    source: str
    external_id: str
    content: str
    rating: Optional[float] = None
    author: Optional[str] = None
    post_date: Optional[datetime] = None


class RawMentionCreate(RawMentionBase):
    pass

class RawMentionResponse(RawMentionBase):
    id: int

    class Config:
        from_attributes = True

class ProcessedMentionBase(BaseModel):
    source_id: int
    brand: str
    source: str
    author: Optional[str] = None
    post_date: Optional[datetime] = None
    cleaned_text: str
    language: Optional[str] = None
    sentiment_label: Optional[str] = None
    sentiment_score: Optional[float] = None

class ProcessedMentionCreate(ProcessedMentionBase):
    pass

class ProcessedMentionResponse(ProcessedMentionBase):
    id: int

    class Config:
        from_attributes = True

class TopicResultBase(BaseModel):
    source_id: int
    brand: str
    topic_id: int
    topic_name: str

class TopicResultCreate(TopicResultBase):
    pass

class TopicResultResponse(TopicResultBase):
    id: int

    class Config:
        from_attributes = True



