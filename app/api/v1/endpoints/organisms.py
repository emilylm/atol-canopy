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
from app.models.organism import Organism, OrganismFetched, OrganismSubmitted, SubmissionStatus
from app.models.user import User
from app.schemas.organism import (
    Organism as OrganismSchema,
    OrganismCreate,
    OrganismFetched as OrganismFetchedSchema,
    OrganismFetchedCreate,
    OrganismSubmitted as OrganismSubmittedSchema,
    OrganismSubmittedCreate,
    OrganismSubmittedUpdate,
    OrganismUpdate,
    SubmissionStatus as SchemaSubmissionStatus,
)

router = APIRouter()


@router.get("/", response_model=List[OrganismSchema])
def read_organisms(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve organisms.
    """
    # All users can read organisms
    organisms = db.query(Organism).offset(skip).limit(limit).all()
    return organisms


@router.post("/", response_model=OrganismSchema)
def create_organism(
    *,
    db: Session = Depends(get_db),
    organism_in: OrganismCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new organism.
    """
    # Only users with 'curator' or 'admin' role can create organisms
    require_role(current_user, ["curator", "admin"])
    
    organism = Organism(
        tax_id=organism_in.tax_id,
        species_taxid_id=organism_in.species_taxid_id,
        scientific_name=organism_in.scientific_name,
        common_name=organism_in.common_name,
        taxonomy_lineage_json=organism_in.taxonomy_lineage_json,
        species_organism_json=organism_in.species_organism_json,
        source_json=organism_in.source_json,
        internal_notes=organism_in.internal_notes,
    )
    db.add(organism)
    db.commit()
    db.refresh(organism)
    return organism


@router.get("/{organism_id}", response_model=OrganismSchema)
def read_organism(
    *,
    db: Session = Depends(get_db),
    organism_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get organism by ID.
    """
    # All users can read organism details
    organism = db.query(Organism).filter(Organism.id == organism_id).first()
    if not organism:
        raise HTTPException(status_code=404, detail="Organism not found")
    return organism


@router.put("/{organism_id}", response_model=OrganismSchema)
def update_organism(
    *,
    db: Session = Depends(get_db),
    organism_id: UUID,
    organism_in: OrganismUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update an organism.
    """
    # Only users with 'curator' or 'admin' role can update organisms
    require_role(current_user, ["curator", "admin"])
    
    organism = db.query(Organism).filter(Organism.id == organism_id).first()
    if not organism:
        raise HTTPException(status_code=404, detail="Organism not found")
    
    update_data = organism_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organism, field, value)
    
    db.add(organism)
    db.commit()
    db.refresh(organism)
    return organism


@router.delete("/{organism_id}", response_model=OrganismSchema)
def delete_organism(
    *,
    db: Session = Depends(get_db),
    organism_id: UUID,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Delete an organism.
    """
    # Only superusers can delete organisms
    organism = db.query(Organism).filter(Organism.id == organism_id).first()
    if not organism:
        raise HTTPException(status_code=404, detail="Organism not found")
    
    db.delete(organism)
    db.commit()
    return organism


# Organism Submitted endpoints
@router.get("/submitted/", response_model=List[OrganismSubmittedSchema])
def read_organism_submissions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[SchemaSubmissionStatus] = Query(None, description="Filter by submission status"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve organism submissions.
    """
    # All users can read organism submissions
    query = db.query(OrganismSubmitted)
    if status:
        query = query.filter(OrganismSubmitted.status == status)
    
    submissions = query.offset(skip).limit(limit).all()
    return submissions


@router.post("/submitted/", response_model=OrganismSubmittedSchema)
def create_organism_submission(
    *,
    db: Session = Depends(get_db),
    submission_in: OrganismSubmittedCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new organism submission.
    """
    # Only users with 'curator' or 'admin' role can create organism submissions
    require_role(current_user, ["curator", "admin"])
    
    submission = OrganismSubmitted(
        organism_id=submission_in.organism_id,
        tax_id=submission_in.tax_id,
        species_taxid_id=submission_in.species_taxid_id,
        scientific_name=submission_in.scientific_name,
        common_name=submission_in.common_name,
        taxonomy_lineage_json=submission_in.taxonomy_lineage_json,
        species_organism_json=submission_in.species_organism_json,
        submitted_json=submission_in.submitted_json,
        internal_json=submission_in.internal_json,
        status=submission_in.status,
        submitted_at=submission_in.submitted_at,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


@router.put("/submitted/{submission_id}", response_model=OrganismSubmittedSchema)
def update_organism_submission(
    *,
    db: Session = Depends(get_db),
    submission_id: UUID,
    submission_in: OrganismSubmittedUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update an organism submission.
    """
    # Only users with 'curator' or 'admin' role can update organism submissions
    require_role(current_user, ["curator", "admin"])
    
    submission = db.query(OrganismSubmitted).filter(OrganismSubmitted.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Organism submission not found")
    
    update_data = submission_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(submission, field, value)
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


# Organism Fetched endpoints
@router.get("/fetched/", response_model=List[OrganismFetchedSchema])
def read_organism_fetches(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve organism fetch records.
    """
    # All users can read organism fetch records
    fetches = db.query(OrganismFetched).offset(skip).limit(limit).all()
    return fetches


@router.post("/fetched/", response_model=OrganismFetchedSchema)
def create_organism_fetch(
    *,
    db: Session = Depends(get_db),
    fetch_in: OrganismFetchedCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new organism fetch record.
    """
    # Only users with 'curator' or 'admin' role can create organism fetch records
    require_role(current_user, ["curator", "admin"])
    
    fetch = OrganismFetched(
        organism_id=fetch_in.organism_id,
        tax_id=fetch_in.tax_id,
        species_taxid_id=fetch_in.species_taxid_id,
        scientific_name=fetch_in.scientific_name,
        common_name=fetch_in.common_name,
        taxonomy_lineage_json=fetch_in.taxonomy_lineage_json,
        species_organism_json=fetch_in.species_organism_json,
        fetched_json=fetch_in.fetched_json,
        fetched_at=fetch_in.fetched_at,
    )
    db.add(fetch)
    db.commit()
    db.refresh(fetch)
    return fetch


@router.get("/fetched/{fetch_id}", response_model=OrganismFetchedSchema)
def read_organism_fetch(
    *,
    db: Session = Depends(get_db),
    fetch_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get organism fetch record by ID.
    """
    # All users can read organism fetch details
    fetch = db.query(OrganismFetched).filter(OrganismFetched.id == fetch_id).first()
    if not fetch:
        raise HTTPException(status_code=404, detail="Organism fetch record not found")
    return fetch
