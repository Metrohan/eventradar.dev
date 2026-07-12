from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from ..core.database import Base


class ScraperLog(Base):
    __tablename__ = "scraper_logs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False)  # 'Youthall', 'Kodluyoruz', etc.
    status = Column(String(50), nullable=False)  # 'success', 'failed'
    events_found = Column(Integer, default=0)
    new_events = Column(Integer, default=0)
    updated_events = Column(Integer, default=0, nullable=False)
    deactivated_events = Column(Integer, default=0, nullable=False)
    failed_events = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    duration_seconds = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f"<ScraperLog {self.source} - {self.status} - {self.created_at}>"
