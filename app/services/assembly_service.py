from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.assembly import Assembly, AssemblyFetched, AssemblySubmitted
from app.schemas.assembly import AssemblyCreate, AssemblyUpdate
from app.services.base_service import BaseService


class AssemblyService(BaseService[Assembly, AssemblyCreate, AssemblyUpdate]):
    """Service for Assembly operations."""
    
    def get_by_experiment_id(self, db: Session, experiment_id: UUID) -> List[Assembly]:
        """Get assemblies by experiment ID."""
        return db.query(Assembly).filter(Assembly.experiment_id == experiment_id).all()
    
    def get_by_assembly_id_serial(self, db: Session, assembly_id_serial: str) -> Optional[Assembly]:
        """Get assembly by assembly ID serial."""
        return db.query(Assembly).filter(Assembly.assembly_id_serial == assembly_id_serial).first()
    
    def get_multi_with_filters(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        experiment_id: Optional[UUID] = None,
        assembly_id_serial: Optional[str] = None,
        assembly_method: Optional[str] = None
    ) -> List[Assembly]:
        """Get assemblies with filters."""
        query = db.query(Assembly)
        if experiment_id:
            query = query.filter(Assembly.experiment_id == experiment_id)
        if assembly_id_serial:
            query = query.filter(Assembly.assembly_id_serial == assembly_id_serial)
        if assembly_method:
            query = query.filter(Assembly.assembly_method == assembly_method)
        return query.offset(skip).limit(limit).all()


class AssemblySubmittedService(BaseService[AssemblySubmitted, AssemblyCreate, AssemblyUpdate]):
    """Service for AssemblySubmitted operations."""
    
    def get_by_assembly_id(self, db: Session, assembly_id: UUID) -> List[AssemblySubmitted]:
        """Get submitted assemblies by assembly ID."""
        return db.query(AssemblySubmitted).filter(AssemblySubmitted.assembly_id == assembly_id).all()


class AssemblyFetchedService(BaseService[AssemblyFetched, AssemblyCreate, AssemblyUpdate]):
    """Service for AssemblyFetched operations."""
    
    def get_by_assembly_id(self, db: Session, assembly_id: UUID) -> List[AssemblyFetched]:
        """Get fetched assemblies by assembly ID."""
        return db.query(AssemblyFetched).filter(AssemblyFetched.assembly_id == assembly_id).all()


assembly_service = AssemblyService(Assembly)
assembly_submitted_service = AssemblySubmittedService(AssemblySubmitted)
assembly_fetched_service = AssemblyFetchedService(AssemblyFetched)
