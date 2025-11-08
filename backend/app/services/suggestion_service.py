from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.suggestion import Suggestion
from ..schemas.suggestion import SuggestionCreate

class SuggestionService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_suggestions(self) -> List[Suggestion]:
        """Get all suggestions ordered by creation date"""
        return self.db.query(Suggestion).order_by(Suggestion.created_at.desc()).all()
    
    def get_suggestion_by_id(self, suggestion_id: int) -> Optional[Suggestion]:
        """Get suggestion by ID"""
        return self.db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
    
    def create_suggestion(self, suggestion_data: SuggestionCreate) -> Suggestion:
        """Create a new suggestion"""
        db_suggestion = Suggestion(
            suggestion_type=suggestion_data.suggestion_type,
            suggestion_title=suggestion_data.suggestion_title,
            suggestion_text=suggestion_data.suggestion_text
        )
        self.db.add(db_suggestion)
        self.db.commit()
        self.db.refresh(db_suggestion)
        return db_suggestion
    
    def delete_suggestion(self, suggestion_id: int) -> bool:
        """Delete a suggestion"""
        db_suggestion = self.get_suggestion_by_id(suggestion_id)
        if not db_suggestion:
            return False
        
        self.db.delete(db_suggestion)
        self.db.commit()
        return True


