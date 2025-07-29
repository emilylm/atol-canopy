from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.read import Read
from app.schemas.read import ReadCreate, ReadUpdate
from app.services.base_service import BaseService


class ReadService(BaseService[Read, ReadCreate, ReadUpdate]):
    """Service for Read operations."""
    
    def get_by_experiment_id(self, db: Session, experiment_id: UUID) -> List[Read]:
        """Get reads by experiment ID."""
        return db.query(Read).filter(Read.experiment_id == experiment_id).all()
    
    def get_by_bpa_dataset_id(self, db: Session, bpa_dataset_id: str) -> List[Read]:
        """Get reads by dataset name."""
        return db.query(Read).filter(Read.bpa_dataset_id == bpa_dataset_id).all()
    
    def get_by_file_name(self, db: Session, file_name: str) -> List[Read]:
        """Get reads by file name."""
        return db.query(Read).filter(Read.file_name == file_name).all()
    
    def get_by_file_md5(self, db: Session, file_md5: str) -> Optional[Read]:
        """Get read by file MD5."""
        return db.query(Read).filter(Read.file_md5 == file_md5).first()
    
    def get_multi_with_filters(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        experiment_id: Optional[UUID] = None,
        bpa_dataset_id: Optional[str] = None,
        file_format: Optional[str] = None
    ) -> List[Read]:
        """Get reads with filters."""
        query = db.query(Read)
        if experiment_id:
            query = query.filter(Read.experiment_id == experiment_id)
        if bpa_dataset_id:
            query = query.filter(Read.bpa_dataset_id == bpa_dataset_id)
        if file_format:
            query = query.filter(Read.file_format == file_format)
        return query.offset(skip).limit(limit).all()


read_service = ReadService(Read)
