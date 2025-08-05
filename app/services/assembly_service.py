from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.assembly import Assembly, AssemblyFetched, AssemblySubmission
from app.schemas.assembly import AssemblyCreate, AssemblyUpdate
from app.services.base_service import BaseService


class AssemblyService(BaseService[Assembly, AssemblyCreate, AssemblyUpdate]):
    """Service for Assembly operations."""
    
    def get_by_experiment_id(self, db: Session, experiment_id: UUID) -> List[Assembly]:
        """Get assemblies by experiment ID."""
        return db.query(Assembly).filter(Assembly.experiment_id == experiment_id).all()
    
    def get_by_assembly_accession(self, db: Session, assembly_accession: str) -> Optional[Assembly]:
        """Get assembly by assembly accession."""
        return db.query(Assembly).filter(Assembly.assembly_accession == assembly_accession).first()
    
    def get_multi_with_filters(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        experiment_id: Optional[UUID] = None,
        assembly_accession: Optional[str] = None,
        assembly_method: Optional[str] = None
    ) -> List[Assembly]:
        """Get assemblies with filters."""
        query = db.query(Assembly)
        if experiment_id:
            query = query.filter(Assembly.experiment_id == experiment_id)
        if assembly_accession:
            query = query.filter(Assembly.assembly_accession == assembly_accession)
        if assembly_method:
            query = query.filter(Assembly.assembly_method == assembly_method)
        return query.offset(skip).limit(limit).all()


class AssemblySubmissionService(BaseService[AssemblySubmission, AssemblyCreate, AssemblyUpdate]):
    """Service for AssemblySubmission operations."""
    
    def get_by_assembly_id(self, db: Session, assembly_id: UUID) -> List[AssemblySubmission]:
        """Get submission assemblies by assembly ID."""
        return db.query(AssemblySubmission).filter(AssemblySubmission.assembly_id == assembly_id).all()


class AssemblyFetchedService(BaseService[AssemblyFetched, AssemblyCreate, AssemblyUpdate]):
    """Service for AssemblyFetched operations."""
    
    def get_by_assembly_id(self, db: Session, assembly_id: UUID) -> List[AssemblyFetched]:
        """Get fetched assemblies by assembly ID."""
        return db.query(AssemblyFetched).filter(AssemblyFetched.assembly_id == assembly_id).all()


assembly_service = AssemblyService(Assembly)
assembly_submission_service = AssemblySubmissionService(AssemblySubmission)
assembly_fetched_service = AssemblyFetchedService(AssemblyFetched)
