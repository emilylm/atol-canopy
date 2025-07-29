import json
import uuid
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_active_user,
    get_current_superuser,
    get_db,
    require_role,
)
from app.models.sample import Sample, SampleFetched, SampleSubmitted
from app.models.organism import Organism
from app.models.experiment import Experiment
from app.models.user import User
from app.schemas.sample import (
    Sample as SampleSchema,
    SampleCreate,
    SampleFetched as SampleFetchedSchema,
    SampleFetchedCreate,
    SampleSubmitted as SampleSubmittedSchema,
    SampleSubmittedCreate,
    SampleSubmittedUpdate,
    SampleUpdate,
    SubmissionStatus as SchemaSubmissionStatus,
)
from app.schemas.bulk_import import BulkSampleImport, BulkImportResponse
from app.schemas.common import SubmittedJsonResponse
import os

router = APIRouter()


@router.get("/", response_model=List[SampleSchema])
def read_samples(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    organism_id: Optional[UUID] = Query(None, description="Filter by organism ID"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve samples.
    """
    # All users can read samples
    query = db.query(Sample)
    if organism_id:
        query = query.filter(Sample.organism_id == organism_id)
    
    samples = query.offset(skip).limit(limit).all()
    return samples


@router.post("/", response_model=SampleSchema)
def create_sample(
    *,
    db: Session = Depends(get_db),
    sample_in: SampleCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new sample.
    """
    # Only users with 'curator' or 'admin' role can create samples
    require_role(current_user, ["curator", "admin"])
    
    sample = Sample(
        organism_id=sample_in.organism_id,
        bpa_sample_id=sample_in.bpa_sample_id,
        sample_accession=sample_in.sample_accession,
        source_json=sample_in.source_json,
    )
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return sample


@router.get("/{sample_id}/submitted-json", response_model=SubmittedJsonResponse)
def get_sample_submitted_json(
    *,
    db: Session = Depends(get_db),
    sample_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get submitted_json for a specific sample.
    """
    sample_submitted = db.query(SampleSubmitted).filter(SampleSubmitted.sample_id == sample_id).first()
    if not sample_submitted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample submitted data not found",
        )
    return {"submitted_json": sample_submitted.submitted_json}


@router.get("/{sample_id}", response_model=SampleSchema)
def read_sample(
    *,
    db: Session = Depends(get_db),
    sample_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get sample by ID.
    """
    # All users can read sample details
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample


@router.put("/{sample_id}", response_model=SampleSchema)
def update_sample(
    *,
    db: Session = Depends(get_db),
    sample_id: UUID,
    sample_in: SampleUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a sample.
    """
    # Only users with 'curator' or 'admin' role can update samples
    require_role(current_user, ["curator", "admin"])
    
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    update_data = sample_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sample, field, value)
    
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return sample


@router.delete("/{sample_id}", response_model=SampleSchema)
def delete_sample(
    *,
    db: Session = Depends(get_db),
    sample_id: UUID,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Delete a sample.
    """
    # Only superusers can delete samples
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    db.delete(sample)
    db.commit()
    return sample


# Sample Submitted endpoints
@router.get("/submitted/", response_model=List[SampleSubmittedSchema])
def read_sample_submissions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[SchemaSubmissionStatus] = Query(None, description="Filter by submission status"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve sample submissions.
    """
    # All users can read sample submissions
    query = db.query(SampleSubmitted)
    if status:
        query = query.filter(SampleSubmitted.status == status)
    
    submissions = query.offset(skip).limit(limit).all()
    return submissions


@router.post("/submitted/", response_model=SampleSubmittedSchema)
def create_sample_submission(
    *,
    db: Session = Depends(get_db),
    submission_in: SampleSubmittedCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new sample submission.
    """
    # Only users with 'curator' or 'admin' role can create sample submissions
    require_role(current_user, ["curator", "admin"])
    
    submission = SampleSubmitted(
        sample_id=submission_in.sample_id,
        organism_id=submission_in.organism_id,
        bpa_sample_id=submission_in.bpa_sample_id,
        sample_accession=submission_in.sample_accession,
        submitted_json=submission_in.submitted_json,
        internal_json=submission_in.internal_json,
        status=submission_in.status,
        submitted_at=submission_in.submitted_at,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


@router.put("/submitted/{submission_id}", response_model=SampleSubmittedSchema)
def update_sample_submission(
    *,
    db: Session = Depends(get_db),
    submission_id: UUID,
    submission_in: SampleSubmittedUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a sample submission.
    """
    # Only users with 'curator' or 'admin' role can update sample submissions
    require_role(current_user, ["curator", "admin"])
    
    submission = db.query(SampleSubmitted).filter(SampleSubmitted.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Sample submission not found")
    
    update_data = submission_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(submission, field, value)
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


# Sample Fetched endpoints
@router.get("/fetched/", response_model=List[SampleFetchedSchema])
def read_sample_fetches(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve sample fetch records.
    """
    # All users can read sample fetch records
    fetches = db.query(SampleFetched).offset(skip).limit(limit).all()
    return fetches


@router.post("/fetched/", response_model=SampleFetchedSchema)
def create_sample_fetch(
    *,
    db: Session = Depends(get_db),
    fetch_in: SampleFetchedCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new sample fetch record.
    """
    # Only users with 'curator' or 'admin' role can create sample fetch records
    require_role(current_user, ["curator", "admin"])
    
    fetch = SampleFetched(
        sample_id=fetch_in.sample_id,
        sample_accession=fetch_in.sample_accession,
        organism_id=fetch_in.organism_id,
        raw_json=fetch_in.raw_json,
        fetched_at=fetch_in.fetched_at,
    )
    db.add(fetch)
    db.commit()
    db.refresh(fetch)
    return fetch

@router.post("/bulk-import", response_model=BulkImportResponse)
def bulk_import_samples(
    *,
    db: Session = Depends(get_db),
    samples_data: Dict[str, Dict[str, Any]],  # Accept direct dictionary format from unique_samples.json
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Bulk import samples from a dictionary keyed by bpa_sample_id.
    
    The request body should directly match the format of the JSON file in data/unique_samples.json,
    which is a dictionary keyed by bpa_sample_id without a wrapping 'samples' key.
    """
    # Only users with 'curator' or 'admin' role can import samples
    require_role(current_user, ["curator", "admin"])
    
    # Load the ENA-ATOL mapping file
    ena_atol_map_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "config", "ena-atol-map.json")
    with open(ena_atol_map_path, "r") as f:
        ena_atol_map = json.load(f)
    
    # Get the sample mapping section
    sample_mapping = ena_atol_map.get("sample", {})
    
    created_samples_count = 0
    created_submitted_count = 0
    skipped_count = 0
    
    for bpa_sample_id, sample_data in samples_data.items():
        # Check if sample already exists
        existing = db.query(Sample).filter(Sample.bpa_sample_id == bpa_sample_id).first()
        if existing:
            skipped_count += 1
            continue
        
        # Get organism reference from sample data
        organism_id = None
        if "organism_grouping_key" in sample_data:
            organism_grouping_key = sample_data["organism_grouping_key"]
            # Look up the organism ID by grouping key
            organism = db.query(Organism).filter(Organism.organism_grouping_key == organism_grouping_key).first()
            if organism:
                organism_id = organism.id
        else:
            print(f"Organism not found for sample {bpa_sample_id}, Skipping")
            skipped_count += 1
            continue
        if not organism:
            print(f"Organism not found with organism_grouping_key {organism_grouping_key}, Skipping")
            skipped_count += 1
            continue
        try:
            # Create new sample
            sample_id = uuid.uuid4()
            sample = Sample(
                id=sample_id,
                organism_id=organism_id,
                bpa_sample_id=bpa_sample_id,
                source_json=sample_data
            )
            db.add(sample)
            
            # Create submitted_json based on the mapping
            submitted_json = {}
            for ena_key, atol_key in sample_mapping.items():
                if atol_key in sample_data:
                    submitted_json[ena_key] = sample_data[atol_key]
            
            # Create sample_submitted record
            sample_submitted = SampleSubmitted(
                id=uuid.uuid4(),
                sample_id=sample_id,
                organism_id=organism_id,
                internal_json=sample_data,
                submitted_json=submitted_json
            )
            db.add(sample_submitted)
            
            db.commit()
            created_samples_count += 1
            created_submitted_count += 1
            
        except Exception as e:
            print(f"Error creating sample with bpa_sample_id: {bpa_sample_id}")
            print(e)
            db.rollback()
            skipped_count += 1
    
    return {
        "created_count": created_samples_count,
        "skipped_count": skipped_count,
        "message": f"Sample import complete. Created samples: {created_samples_count}, "
                  f"Created submitted records: {created_submitted_count}, Skipped: {skipped_count}"
    }


@router.get("/submitted/by-experiment/{bpa_package_id}", response_model=List[SampleSubmittedSchema])
async def get_sample_submitted_by_experiment_package_id(
    bpa_package_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> List[SampleSubmittedSchema]:
    """
    Get SampleSubmitted data for a specific experiment.bpa_package_id.
    
    This endpoint retrieves all submitted sample data associated with a specific experiment BPA package ID.
    """
    # Find the experiment with the given bpa_package_id
    experiment = db.query(Experiment).filter(Experiment.bpa_package_id == bpa_package_id).first()
    if not experiment:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment with bpa_package_id {bpa_package_id} not found"
        )
    
    # Get the sample_id from the experiment
    if not experiment.sample_id:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment with bpa_package_id {bpa_package_id} has no associated sample"
        )
    
    # Find the submitted records for this sample
    submitted_records = db.query(SampleSubmitted).filter(
        SampleSubmitted.sample_id == experiment.sample_id
    ).all()
    
    if not submitted_records:
        raise HTTPException(
            status_code=404,
            detail=f"No submitted sample records found for experiment with bpa_package_id {bpa_package_id}"
        )
    
    return submitted_records
