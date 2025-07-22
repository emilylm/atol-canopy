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
from app.models.bioproject import Bioproject, BioprojectExperiment
from app.models.user import User
from app.schemas.bioproject import (
    Bioproject as BioprojectSchema,
    BioprojectCreate,
    BioprojectExperiment as BioprojectExperimentSchema,
    BioprojectExperimentCreate,
    BioprojectUpdate,
)

router = APIRouter()


@router.get("/", response_model=List[BioprojectSchema])
def read_bioprojects(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve bioprojects.
    """
    # All users can read bioprojects
    bioprojects = db.query(Bioproject).offset(skip).limit(limit).all()
    return bioprojects


@router.post("/", response_model=BioprojectSchema)
def create_bioproject(
    *,
    db: Session = Depends(get_db),
    bioproject_in: BioprojectCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new bioproject.
    """
    # Only users with 'curator' or 'admin' role can create bioprojects
    require_role(current_user, ["curator", "admin"])
    
    bioproject = Bioproject(
        bioproject_accession_vector=bioproject_in.bioproject_accession_vector,
        alias_vector=bioproject_in.alias_vector,
        alias_vector_md5=bioproject_in.alias_vector_md5,
        study_name_vector=bioproject_in.study_name_vector,
        new_study_type=bioproject_in.new_study_type,
        study_abstract_vector=bioproject_in.study_abstract_vector,
    )
    db.add(bioproject)
    db.commit()
    db.refresh(bioproject)
    return bioproject


@router.get("/{bioproject_id}", response_model=BioprojectSchema)
def read_bioproject(
    *,
    db: Session = Depends(get_db),
    bioproject_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get bioproject by ID.
    """
    # All users can read bioproject details
    bioproject = db.query(Bioproject).filter(Bioproject.id == bioproject_id).first()
    if not bioproject:
        raise HTTPException(status_code=404, detail="Bioproject not found")
    return bioproject


@router.put("/{bioproject_id}", response_model=BioprojectSchema)
def update_bioproject(
    *,
    db: Session = Depends(get_db),
    bioproject_id: UUID,
    bioproject_in: BioprojectUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a bioproject.
    """
    # Only users with 'curator' or 'admin' role can update bioprojects
    require_role(current_user, ["curator", "admin"])
    
    bioproject = db.query(Bioproject).filter(Bioproject.id == bioproject_id).first()
    if not bioproject:
        raise HTTPException(status_code=404, detail="Bioproject not found")
    
    update_data = bioproject_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bioproject, field, value)
    
    db.add(bioproject)
    db.commit()
    db.refresh(bioproject)
    return bioproject


@router.delete("/{bioproject_id}", response_model=BioprojectSchema)
def delete_bioproject(
    *,
    db: Session = Depends(get_db),
    bioproject_id: UUID,
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Delete a bioproject.
    """
    # Only superusers can delete bioprojects
    bioproject = db.query(Bioproject).filter(Bioproject.id == bioproject_id).first()
    if not bioproject:
        raise HTTPException(status_code=404, detail="Bioproject not found")
    
    db.delete(bioproject)
    db.commit()
    return bioproject


# Bioproject Experiment endpoints
@router.get("/experiments/", response_model=List[BioprojectExperimentSchema])
def read_bioproject_experiments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    bioproject_id: Optional[UUID] = Query(None, description="Filter by bioproject ID"),
    experiment_id: Optional[UUID] = Query(None, description="Filter by experiment ID"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve bioproject-experiment relationships.
    """
    # All users can read bioproject-experiment relationships
    query = db.query(BioprojectExperiment)
    if bioproject_id:
        query = query.filter(BioprojectExperiment.bioproject_id == bioproject_id)
    if experiment_id:
        query = query.filter(BioprojectExperiment.experiment_id == experiment_id)
    
    relationships = query.offset(skip).limit(limit).all()
    return relationships


@router.post("/experiments/", response_model=BioprojectExperimentSchema)
def create_bioproject_experiment(
    *,
    db: Session = Depends(get_db),
    relationship_in: BioprojectExperimentCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new bioproject-experiment relationship.
    """
    # Only users with 'curator' or 'admin' role can create bioproject-experiment relationships
    require_role(current_user, ["curator", "admin"])
    
    relationship = BioprojectExperiment(
        bioproject_id=relationship_in.bioproject_id,
        experiment_id=relationship_in.experiment_id,
        bioproject_accession_vector=relationship_in.bioproject_accession_vector,
        experiment_id_serial=relationship_in.experiment_id_serial,
    )
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    return relationship


@router.delete("/experiments/{relationship_id}", response_model=BioprojectExperimentSchema)
def delete_bioproject_experiment(
    *,
    db: Session = Depends(get_db),
    relationship_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a bioproject-experiment relationship.
    """
    # Only users with 'curator' or 'admin' role can delete bioproject-experiment relationships
    require_role(current_user, ["curator", "admin"])
    
    relationship = db.query(BioprojectExperiment).filter(BioprojectExperiment.id == relationship_id).first()
    if not relationship:
        raise HTTPException(status_code=404, detail="Bioproject-experiment relationship not found")
    
    db.delete(relationship)
    db.commit()
    return relationship
