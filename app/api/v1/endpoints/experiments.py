import json
import uuid
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_active_user,
    get_current_active_superuser,
    get_db,
    has_role,
)
from app.schemas.common import SubmissionStatus
from app.models.experiment import Experiment, ExperimentFetched, ExperimentSubmitted
from app.models.sample import Sample
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
    SubmissionStatus as SchemaSubmissionStatus,
)
from app.schemas.bulk_import import BulkExperimentImport, BulkImportResponse

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
    if not ("curator" in current_user.roles or "admin" in current_user.roles or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    experiment = Experiment(
        sample_id=experiment_in.sample_id,
        experiment_accession=experiment_in.experiment_accession,
        run_accession=experiment_in.run_accession,
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
    if not ("curator" in current_user.roles or "admin" in current_user.roles or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
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
    current_user: User = Depends(get_current_active_superuser),
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
    status: Optional[SchemaSubmissionStatus] = Query(None, description="Filter by submission status"),
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
    if not ("curator" in current_user.roles or "admin" in current_user.roles or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    submission = ExperimentSubmitted(
        experiment_id=submission_in.experiment_id,
        sample_id=submission_in.sample_id,
        experiment_accession=submission_in.experiment_accession,
        run_accession=submission_in.run_accession,
        submitted_json=submission_in.submitted_json,
        internal_json=submission_in.internal_json,
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
    if not ("curator" in current_user.roles or "admin" in current_user.roles or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
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
    if not ("curator" in current_user.roles or "admin" in current_user.roles or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    fetch = ExperimentFetched(
        experiment_id=fetch_in.experiment_id,
        experiment_accession=fetch_in.experiment_accession,
        run_accession=fetch_in.run_accession,
        sample_id=fetch_in.sample_id,
        raw_json=fetch_in.raw_json,
        fetched_at=fetch_in.fetched_at,
    )
    db.add(fetch)
    db.commit()
    db.refresh(fetch)
    return fetch


@router.post("/bulk-import", response_model=BulkImportResponse)
def bulk_import_experiments(
    *,
    db: Session = Depends(get_db),
    experiments_data: BulkExperimentImport,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Bulk import experiments from a dictionary keyed by package_id.
    
    The request body should match the format of the JSON file in data/experiments.json.
    """
    # Only users with 'curator' or 'admin' role can import experiments
    if not ("curator" in current_user.roles or "admin" in current_user.roles or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    created_experiments_count = 0
    created_submitted_count = 0
    skipped_count = 0
    
    for package_id, experiment_data in experiments_data.experiments.items():
        # Check if experiment data contains sample_name
        if 'sample_name' not in experiment_data:
            skipped_count += 1
            continue
                
        sample_name = experiment_data['sample_name']

        # Get sample id from sample name
        sample = db.query(Sample).filter(Sample.sample_name == sample_name).first()
        if not sample:
            skipped_count += 1
            continue

        try:
            # Check if experiment already exists with this package_id
            existing = db.query(Experiment).filter(Experiment.bpa_package_id == package_id).first()
            if existing:
                skipped_count += 1
                continue
                
            # Create new experiment
            experiment_id = uuid.uuid4()
            experiment = Experiment(
                id=experiment_id,
                sample_id=sample.id,
                bpa_package_id=package_id
            )
            db.add(experiment)
            
            # Create experiment_submitted record
            experiment_submitted = ExperimentSubmitted(
                id=uuid.uuid4(),
                experiment_id=experiment_id,
                sample_id=sample.id,
                internal_json=experiment_data
            )
            db.add(experiment_submitted)
            
            db.commit()
            created_experiments_count += 1
            created_submitted_count += 1
            
        except Exception as e:
            db.rollback()
            skipped_count += 1
    
    return {
        "created_count": created_experiments_count,
        "skipped_count": skipped_count,
        "message": f"Experiment import complete. Created experiments: {created_experiments_count}, "
                  f"Created submitted records: {created_submitted_count}, Skipped: {skipped_count}"
    }
