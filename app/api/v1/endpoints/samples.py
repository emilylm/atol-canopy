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
from app.models.sample import Sample, SampleFetched, SampleRelationship, SampleSubmitted
from app.models.user import User
from app.schemas.sample import (
    Sample as SampleSchema,
    SampleCreate,
    SampleFetched as SampleFetchedSchema,
    SampleFetchedCreate,
    SampleRelationship as SampleRelationshipSchema,
    SampleRelationshipCreate,
    SampleRelationshipUpdate,
    SampleSubmitted as SampleSubmittedSchema,
    SampleSubmittedCreate,
    SampleSubmittedUpdate,
    SampleUpdate,
)

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
        sample_id_serial=sample_in.sample_id_serial,
        organism_id=sample_in.organism_id,
        sample_accession_vector=sample_in.sample_accession_vector,
        source_json=sample_in.source_json,
        internal_notes=sample_in.internal_notes,
        internal_priority_flag=sample_in.internal_priority_flag,
    )
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return sample


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
    status: Optional[str] = Query(None, description="Filter by submission status"),
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
        sample_id_serial=submission_in.sample_id_serial,
        organism_id=submission_in.organism_id,
        submitted_json=submission_in.submitted_json,
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
        sample_id_serial=fetch_in.sample_id_serial,
        sample_accession_vector=fetch_in.sample_accession_vector,
        organism_id=fetch_in.organism_id,
        raw_json=fetch_in.raw_json,
        fetched_at=fetch_in.fetched_at,
    )
    db.add(fetch)
    db.commit()
    db.refresh(fetch)
    return fetch


# Sample Relationship endpoints
@router.get("/relationships/", response_model=List[SampleRelationshipSchema])
def read_sample_relationships(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    source_sample_id: Optional[UUID] = Query(None, description="Filter by source sample ID"),
    target_sample_id: Optional[UUID] = Query(None, description="Filter by target sample ID"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve sample relationships.
    """
    # All users can read sample relationships
    query = db.query(SampleRelationship)
    if source_sample_id:
        query = query.filter(SampleRelationship.source_sample_id == source_sample_id)
    if target_sample_id:
        query = query.filter(SampleRelationship.target_sample_id == target_sample_id)
    
    relationships = query.offset(skip).limit(limit).all()
    return relationships


@router.post("/relationships/", response_model=SampleRelationshipSchema)
def create_sample_relationship(
    *,
    db: Session = Depends(get_db),
    relationship_in: SampleRelationshipCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new sample relationship.
    """
    # Only users with 'curator' or 'admin' role can create sample relationships
    require_role(current_user, ["curator", "admin"])
    
    # Check if both samples exist
    source_sample = db.query(Sample).filter(Sample.id == relationship_in.source_sample_id).first()
    if not source_sample:
        raise HTTPException(status_code=404, detail="Source sample not found")
    
    target_sample = db.query(Sample).filter(Sample.id == relationship_in.target_sample_id).first()
    if not target_sample:
        raise HTTPException(status_code=404, detail="Target sample not found")
    
    relationship = SampleRelationship(
        source_sample_id=relationship_in.source_sample_id,
        target_sample_id=relationship_in.target_sample_id,
        relationship_type=relationship_in.relationship_type,
    )
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    return relationship


@router.put("/relationships/{relationship_id}", response_model=SampleRelationshipSchema)
def update_sample_relationship(
    *,
    db: Session = Depends(get_db),
    relationship_id: UUID,
    relationship_in: SampleRelationshipUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a sample relationship.
    """
    # Only users with 'curator' or 'admin' role can update sample relationships
    require_role(current_user, ["curator", "admin"])
    
    relationship = db.query(SampleRelationship).filter(SampleRelationship.id == relationship_id).first()
    if not relationship:
        raise HTTPException(status_code=404, detail="Sample relationship not found")
    
    update_data = relationship_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(relationship, field, value)
    
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    return relationship


@router.delete("/relationships/{relationship_id}", response_model=SampleRelationshipSchema)
def delete_sample_relationship(
    *,
    db: Session = Depends(get_db),
    relationship_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a sample relationship.
    """
    # Only users with 'curator' or 'admin' role can delete sample relationships
    require_role(current_user, ["curator", "admin"])
    
    relationship = db.query(SampleRelationship).filter(SampleRelationship.id == relationship_id).first()
    if not relationship:
        raise HTTPException(status_code=404, detail="Sample relationship not found")
    
    db.delete(relationship)
    db.commit()
    return relationship
