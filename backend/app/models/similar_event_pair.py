from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class SimilarEventPair(Base):
    __tablename__ = 'similar_event_pairs'
    
    id = Column(Integer, primary_key=True, index=True)
    event1_id = Column(Integer, nullable=False)
    event2_id = Column(Integer, nullable=False)
    similarity_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<SimilarEventPair {self.event1_id}-{self.event2_id}>"


