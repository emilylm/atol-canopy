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
from app.models.read import Read
from app.models.user import User
from app.schemas.read import (
    Read as ReadSchema,
    ReadCreate,
    ReadUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[ReadSchema])
def read_reads(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    experiment_id: Optional[UUID] = Query(None, description="Filter by experiment ID"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve reads.
    """
    # All users can read reads
    query = db.query(Read)
    if experiment_id:
        query = query.filter(Read.experiment_id == experiment_id)
    
    reads = query.offset(skip).limit(limit).all()
    return reads


@router.post("/", response_model=ReadSchema)
def create_read(
    *,
    db: Session = Depends(get_db),
    read_in: ReadCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new read.
    """
    # Only users with 'curator' or 'admin' role can create reads
    require_role(current_user, ["curator", "admin"])
    
    read = Read(
        experiment_id=read_in.experiment_id,
        dataset_name=read_in.dataset_name,
        file_name=read_in.file_name,
        file_format=read_in.file_format,
        file_size=read_in.file_size,
        file_extension_date=read_in.file_extension_date,
        file_md5=read_in.file_md5,
        read_access_date=read_in.read_access_date,
        parameters_url=read_in.parameters_url,
    )
    db.add(read)
    db.commit()
    db.refresh(read)
    return read


@router.get("/{read_id}", response_model=ReadSchema)
def read_read(
    *,
    db: Session = Depends(get_db),
    read_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get read by ID.
    """
    # All users can read read details
    read = db.query(Read).filter(Read.id == read_id).first()
    if not read:
        raise HTTPException(status_code=404, detail="Read not found")
    return read


@router.put("/{read_id}", response_model=ReadSchema)
def update_read(
    *,
    db: Session = Depends(get_db),
    read_id: UUID,
    read_in: ReadUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a read.
    """
    # Only users with 'curator' or 'admin' role can update reads
    require_role(current_user, ["curator", "admin"])
    
    read = db.query(Read).filter(Read.id == read_id).first()
    if not read:
        raise HTTPException(status_code=404, detail="Read not found")
    
    update_data = read_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(read, field, value)
    
    db.add(read)
    db.commit()
    db.refresh(read)
    return read


@router.delete("/{read_id}", response_model=ReadSchema)
def delete_read(
    *,
    db: Session = Depends(get_db),
    read_id: UUID,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Delete a read.
    """
    # Only superusers can delete reads
    read = db.query(Read).filter(Read.id == read_id).first()
    if not read:
        raise HTTPException(status_code=404, detail="Read not found")
    
    db.delete(read)
    db.commit()
    return read
