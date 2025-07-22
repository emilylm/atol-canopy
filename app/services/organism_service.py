from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.organism import Organism, OrganismFetched, OrganismSubmitted
from app.schemas.organism import OrganismCreate, OrganismUpdate
from app.services.base_service import BaseService


class OrganismService(BaseService[Organism, OrganismCreate, OrganismUpdate]):
    """Service for Organism operations."""
    
    def get_by_scientific_name(self, db: Session, scientific_name: str) -> Optional[Organism]:
        """Get organism by scientific name."""
        return db.query(Organism).filter(Organism.scientific_name == scientific_name).first()
    
    def get_by_taxon_id(self, db: Session, taxon_id: str) -> Optional[Organism]:
        """Get organism by taxon ID."""
        return db.query(Organism).filter(Organism.taxon_id == taxon_id).first()
    
    def get_multi_with_filters(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        scientific_name: Optional[str] = None,
        taxon_id: Optional[str] = None
    ) -> List[Organism]:
        """Get organisms with filters."""
        query = db.query(Organism)
        if scientific_name:
            query = query.filter(Organism.scientific_name.ilike(f"%{scientific_name}%"))
        if taxon_id:
            query = query.filter(Organism.taxon_id == taxon_id)
        return query.offset(skip).limit(limit).all()


class OrganismSubmittedService(BaseService[OrganismSubmitted, OrganismCreate, OrganismUpdate]):
    """Service for OrganismSubmitted operations."""
    
    def get_by_organism_id(self, db: Session, organism_id: UUID) -> List[OrganismSubmitted]:
        """Get submitted organisms by organism ID."""
        return db.query(OrganismSubmitted).filter(OrganismSubmitted.organism_id == organism_id).all()


class OrganismFetchedService(BaseService[OrganismFetched, OrganismCreate, OrganismUpdate]):
    """Service for OrganismFetched operations."""
    
    def get_by_organism_id(self, db: Session, organism_id: UUID) -> List[OrganismFetched]:
        """Get fetched organisms by organism ID."""
        return db.query(OrganismFetched).filter(OrganismFetched.organism_id == organism_id).all()


organism_service = OrganismService(Organism)
organism_submitted_service = OrganismSubmittedService(OrganismSubmitted)
organism_fetched_service = OrganismFetchedService(OrganismFetched)
