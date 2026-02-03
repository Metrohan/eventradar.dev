from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from ..models.traffic_log import TrafficLog
from datetime import datetime, timedelta

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def log_request(self, path: str, method: str, ip: str, user_agent: str):
        log = TrafficLog(
            path=path,
            method=method,
            ip_address=ip,
            user_agent=user_agent
        )
        self.db.add(log)
        self.db.commit()

    def get_stats(self, days: int = 30):
        # Time range
        start_date = datetime.now() - timedelta(days=days)
        
        # Daily Traffic (for graph)
        daily_traffic = self.db.query(
            func.date(TrafficLog.timestamp).label('date'),
            func.count(TrafficLog.id).label('count')
        ).filter(
            TrafficLog.timestamp >= start_date
        ).group_by(
            func.date(TrafficLog.timestamp)
        ).order_by(
            func.date(TrafficLog.timestamp)
        ).all()
        
        # Today's count
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = self.db.query(TrafficLog).filter(TrafficLog.timestamp >= today_start).count()
        
        # Total count
        total_count = self.db.query(TrafficLog).count()
        
        # Top Pages
        top_pages = self.db.query(
            TrafficLog.path,
            func.count(TrafficLog.id).label('count')
        ).group_by(
            TrafficLog.path
        ).order_by(
            desc('count')
        ).limit(5).all()
        
        return {
            "daily_traffic": [{"date": str(d.date), "count": d.count} for d in daily_traffic],
            "today_visitors": today_count,
            "total_visitors": total_count,
            "top_pages": [{"path": p.path, "count": p.count} for p in top_pages]
        }
