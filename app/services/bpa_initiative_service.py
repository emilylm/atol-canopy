from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.bpa_initiative import BPAInitiative
from app.schemas.bpa_initiative import BPAInitiativeCreate, BPAInitiativeUpdate
from app.services.base_service import BaseService


class BPAInitiativeService(BaseService[BPAInitiative, BPAInitiativeCreate, BPAInitiativeUpdate]):
    """Service for BPAInitiative operations."""
    
    def get_by_name(self, db: Session, name: str) -> Optional[BPAInitiative]:
        """Get BPA initiative by name."""
        return db.query(BPAInitiative).filter(BPAInitiative.name == name).first()
    
    def get_by_code(self, db: Session, code: str) -> Optional[BPAInitiative]:
        """Get BPA initiative by code."""
        return db.query(BPAInitiative).filter(BPAInitiative.code == code).first()
    
    def get_multi_with_filters(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[BPAInitiative]:
        """Get BPA initiatives with filters."""
        query = db.query(BPAInitiative)
        if is_active is not None:
            query = query.filter(BPAInitiative.is_active == is_active)
        return query.offset(skip).limit(limit).all()


bpa_initiative_service = BPAInitiativeService(BPAInitiative)
