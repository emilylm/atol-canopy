from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.experiment import Experiment, ExperimentFetched, ExperimentSubmitted
from app.schemas.experiment import ExperimentCreate, ExperimentUpdate
from app.services.base_service import BaseService


class ExperimentService(BaseService[Experiment, ExperimentCreate, ExperimentUpdate]):
    """Service for Experiment operations."""
    
    def get_by_sample_id(self, db: Session, sample_id: UUID) -> List[Experiment]:
        """Get experiments by sample ID."""
        return db.query(Experiment).filter(Experiment.sample_id == sample_id).all()
    
    def get_by_experiment_id_serial(self, db: Session, experiment_id_serial: str) -> Optional[Experiment]:
        """Get experiment by experiment ID serial."""
        return db.query(Experiment).filter(Experiment.experiment_id_serial == experiment_id_serial).first()
    
    def get_multi_with_filters(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        sample_id: Optional[UUID] = None,
        experiment_id_serial: Optional[str] = None,
        experiment_type: Optional[str] = None
    ) -> List[Experiment]:
        """Get experiments with filters."""
        query = db.query(Experiment)
        if sample_id:
            query = query.filter(Experiment.sample_id == sample_id)
        if experiment_id_serial:
            query = query.filter(Experiment.experiment_id_serial == experiment_id_serial)
        if experiment_type:
            query = query.filter(Experiment.experiment_type == experiment_type)
        return query.offset(skip).limit(limit).all()


class ExperimentSubmittedService(BaseService[ExperimentSubmitted, ExperimentCreate, ExperimentUpdate]):
    """Service for ExperimentSubmitted operations."""
    
    def get_by_experiment_id(self, db: Session, experiment_id: UUID) -> List[ExperimentSubmitted]:
        """Get submitted experiments by experiment ID."""
        return db.query(ExperimentSubmitted).filter(ExperimentSubmitted.experiment_id == experiment_id).all()


class ExperimentFetchedService(BaseService[ExperimentFetched, ExperimentCreate, ExperimentUpdate]):
    """Service for ExperimentFetched operations."""
    
    def get_by_experiment_id(self, db: Session, experiment_id: UUID) -> List[ExperimentFetched]:
        """Get fetched experiments by experiment ID."""
        return db.query(ExperimentFetched).filter(ExperimentFetched.experiment_id == experiment_id).all()


experiment_service = ExperimentService(Experiment)
experiment_submitted_service = ExperimentSubmittedService(ExperimentSubmitted)
experiment_fetched_service = ExperimentFetchedService(ExperimentFetched)
