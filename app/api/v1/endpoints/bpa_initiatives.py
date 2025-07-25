from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_active_user,
    get_db,
)
from app.models.bpa_initiative import BPAInitiative
from app.models.user import User
from app.schemas.bpa_initiative import (
    BPAInitiative as BPAInitiativeSchema,
    BPAInitiativeCreate,
    BPAInitiativeUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[BPAInitiativeSchema])
def read_bpa_initiatives(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve BPA initiatives.
    """
    # All users can read BPA initiatives
    initiatives = db.query(BPAInitiative).offset(skip).limit(limit).all()
    return initiatives


@router.post("/", response_model=BPAInitiativeSchema)
def create_bpa_initiative(
    *,
    db: Session = Depends(get_db),
    initiative_in: BPAInitiativeCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new BPA initiative.
    """
    # Only users with 'curator' or 'admin' role can create BPA initiatives
    if not ("curator" in current_user.roles or "admin" in current_user.roles or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    initiative = BPAInitiative(
        bpa_initiative_id_serial=initiative_in.bpa_initiative_id_serial,
        name=initiative_in.name,
        shipment_accession=initiative_in.shipment_accession,
    )
    db.add(initiative)
    db.commit()
    db.refresh(initiative)
    return initiative


@router.get("/{initiative_id}", response_model=BPAInitiativeSchema)
def read_bpa_initiative(
    *,
    db: Session = Depends(get_db),
    initiative_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get BPA initiative by ID.
    """
    # All users can read BPA initiative details
    initiative = db.query(BPAInitiative).filter(BPAInitiative.id == initiative_id).first()
    if not initiative:
        raise HTTPException(status_code=404, detail="BPA initiative not found")
    return initiative


@router.put("/{initiative_id}", response_model=BPAInitiativeSchema)
def update_bpa_initiative(
    *,
    db: Session = Depends(get_db),
    initiative_id: UUID,
    initiative_in: BPAInitiativeUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a BPA initiative.
    """
    # Only users with 'curator' or 'admin' role can update BPA initiatives
    if not ("curator" in current_user.roles or "admin" in current_user.roles or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    initiative = db.query(BPAInitiative).filter(BPAInitiative.id == initiative_id).first()
    if not initiative:
        raise HTTPException(status_code=404, detail="BPA initiative not found")
    
    update_data = initiative_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(initiative, field, value)
    
    db.add(initiative)
    db.commit()
    db.refresh(initiative)
    return initiative


@router.delete("/{initiative_id}", response_model=BPAInitiativeSchema)
def delete_bpa_initiative(
    *,
    db: Session = Depends(get_db),
    initiative_id: UUID,
) -> Any:
    """
    Delete a BPA initiative.
    """
    # Only superusers can delete BPA initiatives
    initiative = db.query(BPAInitiative).filter(BPAInitiative.id == initiative_id).first()
    if not initiative:
        raise HTTPException(status_code=404, detail="BPA initiative not found")
    
    db.delete(initiative)
    db.commit()
    return initiative
