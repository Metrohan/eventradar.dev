from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class TrafficLog(Base):
    __tablename__ = 'traffic_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<TrafficLog {self.method} {self.path} at {self.timestamp}>"
