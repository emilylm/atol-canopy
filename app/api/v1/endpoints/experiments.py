from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_active_user,
    get_current_superuser,
    get_db,
    require_role,
)
from app.models.experiment import Experiment, ExperimentFetched, ExperimentSubmitted
from app.models.user import User
from app.schemas.experiment import (
    Experiment as ExperimentSchema,
    ExperimentCreate,
    ExperimentFetched as ExperimentFetchedSchema,
    ExperimentFetchedCreate,
    ExperimentSubmitted as ExperimentSubmittedSchema,
    ExperimentSubmittedCreate,
    ExperimentSubmittedUpdate,
    ExperimentUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[ExperimentSchema])
def read_experiments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    sample_id: Optional[UUID] = Query(None, description="Filter by sample ID"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve experiments.
    """
    # All users can read experiments
    query = db.query(Experiment)
    if sample_id:
        query = query.filter(Experiment.sample_id == sample_id)
    
    experiments = query.offset(skip).limit(limit).all()
    return experiments


@router.post("/", response_model=ExperimentSchema)
def create_experiment(
    *,
    db: Session = Depends(get_db),
    experiment_in: ExperimentCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new experiment.
    """
    # Only users with 'curator' or 'admin' role can create experiments
    require_role(current_user, ["curator", "admin"])
    
    experiment = Experiment(
        experiment_id_serial=experiment_in.experiment_id_serial,
        sample_id=experiment_in.sample_id,
        experiment_accession_vector=experiment_in.experiment_accession_vector,
        run_accession_text=experiment_in.run_accession_text,
        source_json=experiment_in.source_json,
        internal_notes=experiment_in.internal_notes,
        internal_priority_flag=experiment_in.internal_priority_flag,
    )
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment


@router.get("/{experiment_id}", response_model=ExperimentSchema)
def read_experiment(
    *,
    db: Session = Depends(get_db),
    experiment_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get experiment by ID.
    """
    # All users can read experiment details
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment


@router.put("/{experiment_id}", response_model=ExperimentSchema)
def update_experiment(
    *,
    db: Session = Depends(get_db),
    experiment_id: UUID,
    experiment_in: ExperimentUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update an experiment.
    """
    # Only users with 'curator' or 'admin' role can update experiments
    require_role(current_user, ["curator", "admin"])
    
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    update_data = experiment_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(experiment, field, value)
    
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return experiment


@router.delete("/{experiment_id}", response_model=ExperimentSchema)
def delete_experiment(
    *,
    db: Session = Depends(get_db),
    experiment_id: UUID,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Delete an experiment.
    """
    # Only superusers can delete experiments
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    db.delete(experiment)
    db.commit()
    return experiment


# Experiment Submitted endpoints
@router.get("/submitted/", response_model=List[ExperimentSubmittedSchema])
def read_experiment_submissions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by submission status"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve experiment submissions.
    """
    # All users can read experiment submissions
    query = db.query(ExperimentSubmitted)
    if status:
        query = query.filter(ExperimentSubmitted.status == status)
    
    submissions = query.offset(skip).limit(limit).all()
    return submissions


@router.post("/submitted/", response_model=ExperimentSubmittedSchema)
def create_experiment_submission(
    *,
    db: Session = Depends(get_db),
    submission_in: ExperimentSubmittedCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new experiment submission.
    """
    # Only users with 'curator' or 'admin' role can create experiment submissions
    require_role(current_user, ["curator", "admin"])
    
    submission = ExperimentSubmitted(
        experiment_id=submission_in.experiment_id,
        experiment_id_serial=submission_in.experiment_id_serial,
        sample_id=submission_in.sample_id,
        experiment_accession_vector=submission_in.experiment_accession_vector,
        run_accession_text=submission_in.run_accession_text,
        submitted_json=submission_in.submitted_json,
        status=submission_in.status,
        submitted_at=submission_in.submitted_at,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


@router.put("/submitted/{submission_id}", response_model=ExperimentSubmittedSchema)
def update_experiment_submission(
    *,
    db: Session = Depends(get_db),
    submission_id: UUID,
    submission_in: ExperimentSubmittedUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update an experiment submission.
    """
    # Only users with 'curator' or 'admin' role can update experiment submissions
    require_role(current_user, ["curator", "admin"])
    
    submission = db.query(ExperimentSubmitted).filter(ExperimentSubmitted.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Experiment submission not found")
    
    update_data = submission_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(submission, field, value)
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


# Experiment Fetched endpoints
@router.get("/fetched/", response_model=List[ExperimentFetchedSchema])
def read_experiment_fetches(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve experiment fetch records.
    """
    # All users can read experiment fetch records
    fetches = db.query(ExperimentFetched).offset(skip).limit(limit).all()
    return fetches


@router.post("/fetched/", response_model=ExperimentFetchedSchema)
def create_experiment_fetch(
    *,
    db: Session = Depends(get_db),
    fetch_in: ExperimentFetchedCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new experiment fetch record.
    """
    # Only users with 'curator' or 'admin' role can create experiment fetch records
    require_role(current_user, ["curator", "admin"])
    
    fetch = ExperimentFetched(
        experiment_id=fetch_in.experiment_id,
        experiment_id_serial=fetch_in.experiment_id_serial,
        experiment_accession_vector=fetch_in.experiment_accession_vector,
        run_accession_text=fetch_in.run_accession_text,
        sample_id=fetch_in.sample_id,
        raw_json=fetch_in.raw_json,
        fetched_at=fetch_in.fetched_at,
    )
    db.add(fetch)
    db.commit()
    db.refresh(fetch)
    return fetch
