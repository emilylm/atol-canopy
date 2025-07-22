from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.bioproject import Bioproject, BioprojectExperiment
from app.schemas.bioproject import BioprojectCreate, BioprojectExperimentCreate, BioprojectUpdate
from app.services.base_service import BaseService


class BioprojectService(BaseService[Bioproject, BioprojectCreate, BioprojectUpdate]):
    """Service for Bioproject operations."""
    
    def get_by_bioproject_accession(self, db: Session, bioproject_accession: str) -> Optional[Bioproject]:
        """Get bioproject by bioproject accession."""
        return db.query(Bioproject).filter(
            Bioproject.bioproject_accession == bioproject_accession
        ).first()
    
    def get_by_alias(self, db: Session, alias: str) -> List[Bioproject]:
        """Get bioprojects by alias."""
        return db.query(Bioproject).filter(
            Bioproject.alias == alias
        ).all()
    
    def get_by_study_name(self, db: Session, study_name: str) -> List[Bioproject]:
        """Get bioprojects by study name."""
        return db.query(Bioproject).filter(
            Bioproject.study_name.ilike(f"%{study_name}%")
        ).all()
    
    def get_multi_with_filters(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        study_type: Optional[str] = None
    ) -> List[Bioproject]:
        """Get bioprojects with filters."""
        query = db.query(Bioproject)
        if study_type:
            query = query.filter(Bioproject.new_study_type == study_type)
        return query.offset(skip).limit(limit).all()


class BioprojectExperimentService(BaseService[BioprojectExperiment, BioprojectExperimentCreate, BioprojectExperimentCreate]):
    """Service for BioprojectExperiment operations."""
    
    def get_by_bioproject_id(self, db: Session, bioproject_id: UUID) -> List[BioprojectExperiment]:
        """Get bioproject-experiment relationships by bioproject ID."""
        return db.query(BioprojectExperiment).filter(BioprojectExperiment.bioproject_id == bioproject_id).all()
    
    def get_by_experiment_id(self, db: Session, experiment_id: UUID) -> List[BioprojectExperiment]:
        """Get bioproject-experiment relationships by experiment ID."""
        return db.query(BioprojectExperiment).filter(BioprojectExperiment.experiment_id == experiment_id).all()


bioproject_service = BioprojectService(Bioproject)
bioproject_experiment_service = BioprojectExperimentService(BioprojectExperiment)
