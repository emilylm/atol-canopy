import json
import uuid
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_current_superuser, get_db, require_role
from app.models.experiment import Experiment, ExperimentSubmitted
from app.models.sample import Sample
from app.models.user import User
from app.schemas.bulk_import import BulkImportResponse
from app.schemas.experiment import (
    ExperimentCreate,
    Experiment as ExperimentSchema,
    ExperimentUpdate,
    ExperimentSubmitted as ExperimentSubmittedSchema,
    ExperimentFetched as ExperimentFetchedSchema,
    ExperimentFetchedCreate,
    ExperimentSubmittedCreate,
    ExperimentSubmittedUpdate,
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
    require_role(current_user, ["curator", "admin"])
    
    experiment = Experiment(
        sample_id=experiment_in.sample_id,
        experiment_accession=experiment_in.experiment_accession,
        run_accession=experiment_in.run_accession,
        source_json=experiment_in.source_json,
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
    require_role(current_user, ["curator", "admin"])
    
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
    experiments_data: Dict[str, Dict[str, Any]],  # Accept direct dictionary format from experiments.json
    current_user: User = Depends(get_current_active_user),
) -> BulkImportResponse:
    """
    Bulk import experiments from a dictionary keyed by package_id.
    
    The request body should directly match the format of the JSON file in data/experiments.json,
    which is a dictionary keyed by package_id without a wrapping 'experiments' key.
    """
    # Only users with 'curator' or 'admin' role can import experiments
    require_role(current_user, ["curator", "admin"])
    
    created_experiments_count = 0
    created_submitted_count = 0
    skipped_count = 0
    
    # Add debug counters
    missing_bpa_sample_id_count = 0
    missing_sample_count = 0
    existing_experiment_count = 0
    missing_required_fields_count = 0
    
    for package_id, experiment_data in experiments_data.items():
        # Check if experiment data contains bpa_sample_id
        if 'bpa_sample_id' not in experiment_data:
            print(f"bpa_sample_id missing for package: {package_id}")
            missing_bpa_sample_id_count += 1
            skipped_count += 1
            continue
                
        bpa_sample_id = experiment_data['bpa_sample_id']
        if not bpa_sample_id:
            print(f"bpa_sample_id missing for package: {package_id}")
            missing_sample_count += 1
            skipped_count += 1
            continue

        sample_id = None
        # Get sample id from sample name
        sample = db.query(Sample).filter(Sample.bpa_sample_id == bpa_sample_id).first()
        if not sample:
            print(f"Sample not found for bpa_sample_id: {bpa_sample_id}")
            missing_sample_count += 1
            skipped_count += 1
            continue
        sample_id = sample.id

        try:
            # Check if experiment already exists with this package_id
            existing = db.query(Experiment).filter(Experiment.bpa_package_id == package_id).first()
            if existing:
                print(f"Experiment already exists with package: {package_id}")
                existing_experiment_count += 1
                skipped_count += 1
                continue
                
            # Add additional fields from experiment_data that might be useful
            experiment_accession = experiment_data.get('experiment_accession')
            run_accession = experiment_data.get('run_accession')
                
            # Create new experiment
            experiment_id = uuid.uuid4()
            experiment = Experiment(
                id=experiment_id,
                sample_id=sample_id,
                bpa_package_id=package_id,
                experiment_accession=experiment_accession,
                run_accession=run_accession,
                source_json=experiment_data
            )
            db.add(experiment)
            
            # Create experiment_submitted record
            experiment_submitted = ExperimentSubmitted(
                id=uuid.uuid4(),
                experiment_id=experiment_id,
                sample_id=sample_id,
                internal_json=experiment_data
            )
            db.add(experiment_submitted)
            
            db.commit()
            created_experiments_count += 1
            created_submitted_count += 1
            
        except Exception as e:
            print(f"Error creating experiment with package_id: {package_id}, bpa_sample_id: {bpa_sample_id}")
            print(e)
            db.rollback()
            skipped_count += 1
    
    return {
        "created_count": created_experiments_count,
        "skipped_count": skipped_count,
        "message": f"Experiment import complete. Created experiments: {created_experiments_count}, Created submitted records: {created_submitted_count}, Skipped: {skipped_count}",
        "debug": {
            "missing_bpa_sample_id": missing_bpa_sample_id_count,
            "missing_sample": missing_sample_count,
            "existing_experiment": existing_experiment_count,
            "missing_required_fields": missing_required_fields_count
        }
    }


@router.get("/submitted/{bpa_package_id}", response_model=ExperimentSubmittedSchema)
async def get_experiment_submitted_by_package_id(
    bpa_package_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ExperimentSubmittedSchema:
    """
    Get ExperimentSubmitted data for a specific bpa_package_id.
    
    This endpoint retrieves the submitted experiment data associated with a specific BPA package ID.
    """
    # Find the experiment with the given bpa_package_id
    experiment = db.query(Experiment).filter(Experiment.bpa_package_id == bpa_package_id).first()
    if not experiment:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment with bpa_package_id {bpa_package_id} not found"
        )
    
    # Find the submitted record for this experiment
    submitted_record = db.query(ExperimentSubmitted).filter(
        ExperimentSubmitted.experiment_id == experiment.id
    ).first()
    
    if not submitted_record:
        raise HTTPException(
            status_code=404,
            detail=f"No submitted record found for experiment with bpa_package_id {bpa_package_id}"
        )
    
    return submitted_record
