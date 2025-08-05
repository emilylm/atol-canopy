from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.sample import Sample, SampleFetched, SampleSubmission
from app.schemas.sample import SampleCreate, SampleUpdate
from app.services.base_service import BaseService


class SampleService(BaseService[Sample, SampleCreate, SampleUpdate]):
    """Service for Sample operations."""
    
    def get_by_organism_id(self, db: Session, organism_id: UUID) -> List[Sample]:
        """Get samples by organism ID."""
        return db.query(Sample).filter(Sample.organism_id == organism_id).all()
    
    def get_by_bpa_sample_id(self, db: Session, bpa_sample_id: str) -> Optional[Sample]:
        """Get sample by sample name."""
        return db.query(Sample).filter(Sample.bpa_sample_id == bpa_sample_id).first()
    
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
        bpa_sample_id: Optional[str] = None,
        sample_accession: Optional[str] = None,
        tissue_type: Optional[str] = None
    ) -> List[Sample]:
        """Get samples with filters."""
        query = db.query(Sample)
        if organism_id:
            query = query.filter(Sample.organism_id == organism_id)
        if bpa_sample_id:
            query = query.filter(Sample.bpa_sample_id.ilike(f"%{bpa_sample_id}%"))
        if sample_accession:
            query = query.filter(Sample.sample_accession == sample_accession)
        if tissue_type:
            query = query.filter(Sample.tissue_type == tissue_type)
        return query.offset(skip).limit(limit).all()


class SampleSubmissionService(BaseService[SampleSubmission, SampleCreate, SampleUpdate]):
    """Service for SampleSubmission operations."""
    
    def get_by_sample_id(self, db: Session, sample_id: UUID) -> List[SampleSubmission]:
        """Get submission samples by sample ID."""
        return db.query(SampleSubmission).filter(SampleSubmission.sample_id == sample_id).all()


class SampleFetchedService(BaseService[SampleFetched, SampleCreate, SampleUpdate]):
    """Service for SampleFetched operations."""
    
    def get_by_sample_id(self, db: Session, sample_id: UUID) -> List[SampleFetched]:
        """Get fetched samples by sample ID."""
        return db.query(SampleFetched).filter(SampleFetched.sample_id == sample_id).all()


sample_service = SampleService(Sample)
sample_submission_service = SampleSubmissionService(SampleSubmission)
sample_fetched_service = SampleFetchedService(SampleFetched)
