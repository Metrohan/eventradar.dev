from sqlalchemy.orm import Session
from ..models.subscriber import Subscriber
from ..schemas.subscriber import BroadcastRequest
from typing import List

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_subscribers(self) -> List[Subscriber]:
        return self.db.query(Subscriber).all()

    def get_stats(self):
        total = self.db.query(Subscriber).count()
        telegram = self.db.query(Subscriber).filter(Subscriber.channel == 'telegram').count()
        email = self.db.query(Subscriber).filter(Subscriber.channel == 'email').count()
        active = self.db.query(Subscriber).filter(Subscriber.is_active == True).count()
        
        return {
            "total_subscribers": total,
            "telegram_count": telegram,
            "email_count": email,
            "active_count": active
        }

    def broadcast_message(self, request: BroadcastRequest) -> dict:
        """
        Simulate broadcasting a message.
        In production, this would connect to Telegram Bot API / SMTP.
        """
        query = self.db.query(Subscriber).filter(Subscriber.is_active == True)
        
        if request.target_channel != 'all':
            query = query.filter(Subscriber.channel == request.target_channel)
            
        # Mock filtering by interest (JSON contains)
        # Note: SQLite/Postgres JSON filtering varies, keeping it simple for mock
        subscribers = query.all()
        
        count = 0
        for sub in subscribers:
            if request.target_interest and request.target_interest not in sub.interests:
                continue
            
            # TODO: Actual Send Logic
            # send_telegram(sub.contact_info, request.message)
            count += 1
            
        return {
            "status": "success",
            "message": f"Message queued for {count} subscribers",
            "recipient_count": count
        }
