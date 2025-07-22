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
    
    def get_by_sample_name(self, db: Session, sample_name: str) -> Optional[Sample]:
        """Get sample by sample name."""
        return db.query(Sample).filter(Sample.sample_name == sample_name).first()
    
    def get_by_sample_accession(self, db: Session, sample_accession: str) -> Optional[Sample]:
        """Get sample by sample accession."""
        return db.query(Sample).filter(Sample.sample_accession == sample_accession).first()
    
    def get_multi_with_filters(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        organism_id: Optional[UUID] = None,
        sample_name: Optional[str] = None,
        sample_accession: Optional[str] = None,
        tissue_type: Optional[str] = None
    ) -> List[Sample]:
        """Get samples with filters."""
        query = db.query(Sample)
        if organism_id:
            query = query.filter(Sample.organism_id == organism_id)
        if sample_name:
            query = query.filter(Sample.sample_name.ilike(f"%{sample_name}%"))
        if sample_accession:
            query = query.filter(Sample.sample_accession == sample_accession)
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
