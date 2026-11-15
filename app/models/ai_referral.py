from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..core.database import Base


class AiReferral(Base):
    """One page view that an AI assistant sent: a label, a path and a time."""

    __tablename__ = "ai_referrals"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(32), nullable=False)  # chatgpt, claude, perplexity...
    path = Column(String(255), nullable=False)  # landing page, no query string
    timestamp = Column(DateTime, default=func.now(), nullable=False, index=True)

    def __repr__(self):
        return f"<AiReferral {self.source} {self.path} at {self.timestamp}>"
