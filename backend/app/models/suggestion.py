from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class Suggestion(Base):
    __tablename__ = 'suggestions'
    
    id = Column(Integer, primary_key=True, index=True)
    suggestion_type = Column(String(50))
    suggestion_text = Column(Text)
    suggestion_title = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<Suggestion {self.suggestion_title}>"


