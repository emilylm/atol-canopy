import uuid
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.common import SubmissionStatus

from app.core.dependencies import (
    get_current_active_user,
    get_db,
)
from app.models.organism import Organism
from app.models.user import User
from app.schemas.organism import (
    Organism as OrganismSchema,
    OrganismCreate,
    OrganismUpdate,
    SubmissionStatus as SchemaSubmissionStatus,
)
from app.schemas.bulk_import import BulkOrganismImport, BulkImportResponse

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
    if not ("curator" in current_user.roles or "admin" in current_user.roles or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
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
    if not ("curator" in current_user.roles or "admin" in current_user.roles or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
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


@router.post("/bulk-import", response_model=BulkImportResponse)
def bulk_import_organisms(
    *,
    db: Session = Depends(get_db),
    organisms_data: BulkOrganismImport,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Bulk import organisms from a dictionary keyed by organism_grouping_key.
    
    The request body should match the format of the JSON file in data/unique_organisms.json.
    """
    # Only users with 'curator' or 'admin' role can import organisms
    if not ("curator" in current_user.roles or "admin" in current_user.roles or current_user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    created_count = 0
    skipped_count = 0
    
    for organism_grouping_key, organism_data in organisms_data.organisms.items():
        # Extract tax_id from the organism data
        if "taxon_id" in organism_data:
            tax_id = organism_data["taxon_id"]
        else:
            skipped_count += 1
            continue
        
        # Check if organism already exists by grouping key
        existing = db.query(Organism).filter(Organism.organism_grouping_key == organism_grouping_key).first()
        if existing:
            skipped_count += 1
            continue
        
        # Create new organism
        scientific_name = organism_data.get("scientific_name")
        if not scientific_name:
            skipped_count += 1
            continue
        
        try:
            # Create new organism
            organism = Organism(
                id=uuid.uuid4(),
                organism_grouping_key=organism_grouping_key,
                tax_id=tax_id,
                scientific_name=scientific_name,
                bpa_json=organism_data
            )
            db.add(organism)
            db.commit()
            created_count += 1
        except Exception as e:
            db.rollback()
            skipped_count += 1
    
    return {
        "created_count": created_count,
        "skipped_count": skipped_count,
        "message": f"Organism import complete. Created: {created_count}, Skipped: {skipped_count}"
    }
