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


from app.models.assembly import Assembly, AssemblyFetched, AssemblySubmitted
from app.models.user import User

from app.schemas.assembly import (
    Assembly as AssemblySchema,
    AssemblyCreate,
    AssemblyFetched as AssemblyFetchedSchema,
    AssemblyFetchedCreate,
    AssemblySubmitted as AssemblySubmittedSchema,
    AssemblySubmittedCreate,
    AssemblySubmittedUpdate,
    AssemblyUpdate,
    SubmissionStatus as SchemaSubmissionStatus,
)

router = APIRouter()


@router.get("/", response_model=List[AssemblySchema])
def read_assemblies(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    organism_id: Optional[UUID] = Query(None, description="Filter by organism ID"),
    sample_id: Optional[UUID] = Query(None, description="Filter by sample ID"),
    experiment_id: Optional[UUID] = Query(None, description="Filter by experiment ID"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve assemblies.
    """
    # All users can read assemblies
    query = db.query(Assembly)
    if organism_id:
        query = query.filter(Assembly.organism_id == organism_id)
    if sample_id:
        query = query.filter(Assembly.sample_id == sample_id)
    if experiment_id:
        query = query.filter(Assembly.experiment_id == experiment_id)
    
    assemblies = query.offset(skip).limit(limit).all()
    return assemblies


@router.post("/", response_model=AssemblySchema)
def create_assembly(
    *,
    db: Session = Depends(get_db),
    assembly_in: AssemblyCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new assembly.
    """
    # Only users with 'curator' or 'admin' role can create assemblies
    if not ("curator" in current_user.roles or "admin" in current_user.roles or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    assembly = Assembly(
        organism_id=assembly_in.organism_id,
        sample_id=assembly_in.sample_id,
        experiment_id=assembly_in.experiment_id,
        assembly_accession=assembly_in.assembly_accession,
        source_json=assembly_in.source_json,
        internal_notes=assembly_in.internal_notes,
    )
    db.add(assembly)
    db.commit()
    db.refresh(assembly)
    return assembly


@router.get("/{assembly_id}", response_model=AssemblySchema)
def read_assembly(
    *,
    db: Session = Depends(get_db),
    assembly_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get assembly by ID.
    """
    # All users can read assembly details
    assembly = db.query(Assembly).filter(Assembly.id == assembly_id).first()
    if not assembly:
        raise HTTPException(status_code=404, detail="Assembly not found")
    return assembly


@router.put("/{assembly_id}", response_model=AssemblySchema)
def update_assembly(
    *,
    db: Session = Depends(get_db),
    assembly_id: UUID,
    assembly_in: AssemblyUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update an assembly.
    """
    # Only users with 'curator' or 'admin' role can update assemblies
    if not ("curator" in current_user.roles or "admin" in current_user.roles or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    assembly = db.query(Assembly).filter(Assembly.id == assembly_id).first()
    if not assembly:
        raise HTTPException(status_code=404, detail="Assembly not found")
    
    update_data = assembly_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assembly, field, value)
    
    db.add(assembly)
    db.commit()
    db.refresh(assembly)
    return assembly


@router.delete("/{assembly_id}", response_model=AssemblySchema)
def delete_assembly(
    *,
    db: Session = Depends(get_db),
    assembly_id: UUID,
) -> Any:
    """
    Delete an assembly.
    """
    # Only superusers can delete assemblies
    assembly = db.query(Assembly).filter(Assembly.id == assembly_id).first()
    if not assembly:
        raise HTTPException(status_code=404, detail="Assembly not found")
    
    db.delete(assembly)
    db.commit()
    return assembly


# Assembly Submitted endpoints
@router.get("/submitted/", response_model=List[AssemblySubmittedSchema])
def read_assembly_submissions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[SchemaSubmissionStatus] = Query(None, description="Filter by submission status"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve assembly submissions.
    """
    # All users can read assembly submissions
    query = db.query(AssemblySubmitted)
    if status:
        query = query.filter(AssemblySubmitted.status == status)
    
    submissions = query.offset(skip).limit(limit).all()
    return submissions


@router.post("/submitted/", response_model=AssemblySubmittedSchema)
def create_assembly_submission(
    *,
    db: Session = Depends(get_db),
    submission_in: AssemblySubmittedCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new assembly submission.
    """
    # Only users with 'curator' or 'admin' role can create assembly submissions
    if not ("curator" in current_user.roles or "admin" in current_user.roles or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    submission = AssemblySubmitted(
        assembly_id=submission_in.assembly_id,
        organism_id=submission_in.organism_id,
        sample_id=submission_in.sample_id,
        experiment_id=submission_in.experiment_id,
        assembly_accession=submission_in.assembly_accession,
        submitted_json=submission_in.submitted_json,
        internal_json=submission_in.internal_json,
        status=submission_in.status,
        submitted_at=submission_in.submitted_at,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


@router.put("/submitted/{submission_id}", response_model=AssemblySubmittedSchema)
def update_assembly_submission(
    *,
    db: Session = Depends(get_db),
    submission_id: UUID,
    submission_in: AssemblySubmittedUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update an assembly submission.
    """
    # Only users with 'curator' or 'admin' role can update assembly submissions
    if not ("curator" in current_user.roles or "admin" in current_user.roles or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    submission = db.query(AssemblySubmitted).filter(AssemblySubmitted.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Assembly submission not found")
    
    update_data = submission_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(submission, field, value)
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


# Assembly Fetched endpoints
@router.get("/fetched/", response_model=List[AssemblyFetchedSchema])
def read_assembly_fetches(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve assembly fetch records.
    """
    # All users can read assembly fetch records
    fetches = db.query(AssemblyFetched).offset(skip).limit(limit).all()
    return fetches


@router.post("/fetched/", response_model=AssemblyFetchedSchema)
def create_assembly_fetch(
    *,
    db: Session = Depends(get_db),
    fetch_in: AssemblyFetchedCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new assembly fetch record.
    """
    # Only users with 'curator' or 'admin' role can create assembly fetch records
    if not ("curator" in current_user.roles or "admin" in current_user.roles or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    fetch = AssemblyFetched(
        assembly_id=fetch_in.assembly_id,
        assembly_accession=fetch_in.assembly_accession,
        organism_id=fetch_in.organism_id,
        sample_id=fetch_in.sample_id,
        experiment_id=fetch_in.experiment_id,
        fetched_json=fetch_in.fetched_json,
        fetched_at=fetch_in.fetched_at,
    )
    db.add(fetch)
    db.commit()
    db.refresh(fetch)
    return fetch
