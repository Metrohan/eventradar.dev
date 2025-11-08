from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.announcement import Announcement
from ..schemas.announcement import AnnouncementCreate

class AnnouncementService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_announcements(self) -> List[Announcement]:
        """Get all announcements ordered by creation date"""
        return self.db.query(Announcement).order_by(Announcement.created_at.desc()).all()
    
    def get_latest_announcement(self) -> Optional[Announcement]:
        """Get the latest announcement"""
        return self.db.query(Announcement).order_by(Announcement.created_at.desc()).first()
    
    def get_announcement_by_id(self, announcement_id: int) -> Optional[Announcement]:
        """Get announcement by ID"""
        return self.db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    def create_announcement(self, announcement_data: AnnouncementCreate) -> Announcement:
        """Create a new announcement"""
        db_announcement = Announcement(
            title=announcement_data.title,
            message=announcement_data.message
        )
        self.db.add(db_announcement)
        self.db.commit()
        self.db.refresh(db_announcement)
        return db_announcement
    
    def delete_announcement(self, announcement_id: int) -> bool:
        """Delete an announcement"""
        db_announcement = self.get_announcement_by_id(announcement_id)
        if not db_announcement:
            return False
        
        self.db.delete(db_announcement)
        self.db.commit()
        return True


