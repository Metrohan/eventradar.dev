from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from ..core.database import Base


class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, index=True)
    contact_info = Column(String(255), nullable=False)  # email or chat_id
    channel = Column(String(50), nullable=False)  # 'telegram', 'email'
    interests = Column(JSON, default=list)  # e.g. ["python", "react"]
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Subscriber {self.channel}:{self.contact_info}>"
