from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.sample import Sample, SampleFetched, SampleRelationship, SampleSubmitted
from app.schemas.sample import SampleCreate, SampleRelationshipCreate, SampleUpdate
from app.services.base_service import BaseService


class SampleService(BaseService[Sample, SampleCreate, SampleUpdate]):
    """Service for Sample operations."""
    
    def get_by_organism_id(self, db: Session, organism_id: UUID) -> List[Sample]:
        """Get samples by organism ID."""
        return db.query(Sample).filter(Sample.organism_id == organism_id).all()
    
    def get_by_sample_id_serial(self, db: Session, sample_id_serial: str) -> Optional[Sample]:
        """Get sample by sample ID serial."""
        return db.query(Sample).filter(Sample.sample_id_serial == sample_id_serial).first()
    
    def get_multi_with_filters(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        organism_id: Optional[UUID] = None,
        sample_id_serial: Optional[str] = None,
        tissue_type: Optional[str] = None
    ) -> List[Sample]:
        """Get samples with filters."""
        query = db.query(Sample)
        if organism_id:
            query = query.filter(Sample.organism_id == organism_id)
        if sample_id_serial:
            query = query.filter(Sample.sample_id_serial == sample_id_serial)
        if tissue_type:
            query = query.filter(Sample.tissue_type == tissue_type)
        return query.offset(skip).limit(limit).all()


class SampleSubmittedService(BaseService[SampleSubmitted, SampleCreate, SampleUpdate]):
    """Service for SampleSubmitted operations."""
    
    def get_by_sample_id(self, db: Session, sample_id: UUID) -> List[SampleSubmitted]:
        """Get submitted samples by sample ID."""
        return db.query(SampleSubmitted).filter(SampleSubmitted.sample_id == sample_id).all()


class SampleFetchedService(BaseService[SampleFetched, SampleCreate, SampleUpdate]):
    """Service for SampleFetched operations."""
    
    def get_by_sample_id(self, db: Session, sample_id: UUID) -> List[SampleFetched]:
        """Get fetched samples by sample ID."""
        return db.query(SampleFetched).filter(SampleFetched.sample_id == sample_id).all()


class SampleRelationshipService(BaseService[SampleRelationship, SampleRelationshipCreate, SampleRelationshipCreate]):
    """Service for SampleRelationship operations."""
    
    def get_by_sample_id(self, db: Session, sample_id: UUID) -> List[SampleRelationship]:
        """Get sample relationships by sample ID."""
        return db.query(SampleRelationship).filter(
            (SampleRelationship.sample_id == sample_id) | 
            (SampleRelationship.related_sample_id == sample_id)
        ).all()
    
    def get_by_relationship_type(self, db: Session, relationship_type: str) -> List[SampleRelationship]:
        """Get sample relationships by relationship type."""
        return db.query(SampleRelationship).filter(
            SampleRelationship.relationship_type == relationship_type
        ).all()


sample_service = SampleService(Sample)
sample_submitted_service = SampleSubmittedService(SampleSubmitted)
sample_fetched_service = SampleFetchedService(SampleFetched)
sample_relationship_service = SampleRelationshipService(SampleRelationship)
