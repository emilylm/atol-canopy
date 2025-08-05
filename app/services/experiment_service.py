from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.experiment import Experiment, ExperimentFetched, ExperimentSubmission
from app.schemas.experiment import ExperimentCreate, ExperimentUpdate
from app.services.base_service import BaseService


class ExperimentService(BaseService[Experiment, ExperimentCreate, ExperimentUpdate]):
    """Service for Experiment operations."""
    
    def get_by_sample_id(self, db: Session, sample_id: UUID) -> List[Experiment]:
        """Get experiments by sample ID."""
        return db.query(Experiment).filter(Experiment.sample_id == sample_id).all()
    
    def get_by_experiment_accession(self, db: Session, experiment_accession: str) -> Optional[Experiment]:
        """Get experiment by experiment accession."""
        return db.query(Experiment).filter(Experiment.experiment_accession == experiment_accession).first()
    
    def get_by_run_accession(self, db: Session, run_accession: str) -> Optional[Experiment]:
        """Get experiment by run accession."""
        return db.query(Experiment).filter(Experiment.run_accession == run_accession).first()
    
    def get_multi_with_filters(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        sample_id: Optional[UUID] = None,
        experiment_accession: Optional[str] = None,
        run_accession: Optional[str] = None,
        experiment_type: Optional[str] = None
    ) -> List[Experiment]:
        """Get experiments with filters."""
        query = db.query(Experiment)
        if sample_id:
            query = query.filter(Experiment.sample_id == sample_id)
        if experiment_accession:
            query = query.filter(Experiment.experiment_accession == experiment_accession)
        if run_accession:
            query = query.filter(Experiment.run_accession == run_accession)
        if experiment_type:
            query = query.filter(Experiment.experiment_type == experiment_type)
        return query.offset(skip).limit(limit).all()


class ExperimentSubmissionService(BaseService[ExperimentSubmission, ExperimentCreate, ExperimentUpdate]):
    """Service for ExperimentSubmission operations."""
    
    def get_by_experiment_id(self, db: Session, experiment_id: UUID) -> List[ExperimentSubmission]:
        """Get submission experiments by experiment ID."""
        return db.query(ExperimentSubmission).filter(ExperimentSubmission.experiment_id == experiment_id).all()


class ExperimentFetchedService(BaseService[ExperimentFetched, ExperimentCreate, ExperimentUpdate]):
    """Service for ExperimentFetched operations."""
    
    def get_by_experiment_id(self, db: Session, experiment_id: UUID) -> List[ExperimentFetched]:
        """Get fetched experiments by experiment ID."""
        return db.query(ExperimentFetched).filter(ExperimentFetched.experiment_id == experiment_id).all()


experiment_service = ExperimentService(Experiment)
experiment_submission_service = ExperimentSubmissionService(ExperimentSubmission)
experiment_fetched_service = ExperimentFetchedService(ExperimentFetched)
