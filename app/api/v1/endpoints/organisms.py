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
        scientific_name=organism_in.scientific_name,
        common_name=organism_in.common_name,
        common_name_source=organism_in.common_name_source,
        taxonomy_lineage_json=organism_in.taxonomy_lineage_json,
        bpa_json=organism_in.bpa_json,
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
