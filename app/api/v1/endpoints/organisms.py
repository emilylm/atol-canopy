import uuid
from typing import Any, List, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_current_active_user,
    get_current_superuser,
    get_db,
    require_role,
)
from app.models.organism import Organism
from app.models.sample import Sample, SampleSubmitted
from app.models.experiment import Experiment, ExperimentSubmitted
from app.models.read import Read
from app.models.user import User
from app.schemas.organism import (
    Organism as OrganismSchema,
    OrganismCreate,
    OrganismUpdate,
)
from app.schemas.bulk_import import BulkOrganismImport, BulkImportResponse
from app.schemas.aggregate import OrganismSubmittedJsonResponse, SampleSubmittedJson, ExperimentSubmittedJson, ReadSubmittedJson

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


@router.get("/grouping-key/{organism_grouping_key}/submitted-json", response_model=OrganismSubmittedJsonResponse)
def get_organism_submitted_json(
    *,
    db: Session = Depends(get_db),
    organism_grouping_key: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get all submitted_json data for samples, experiments, and reads related to a specific organism_grouping_key.
    """
    # Find the organism by grouping key
    organism = db.query(Organism).filter(Organism.organism_grouping_key == organism_grouping_key).first()
    if not organism:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organism with grouping key '{organism_grouping_key}' not found",
        )
    
    # Initialize response object
    response = OrganismSubmittedJsonResponse(
        organism_id=organism.id,
        organism_grouping_key=organism.organism_grouping_key,
        scientific_name=organism.scientific_name,
        common_name=organism.common_name,
        samples=[],
        experiments=[],
        reads=[]
    )
    
    # Get samples for this organism
    samples = db.query(Sample).filter(Sample.organism_id == organism.id).all()
    sample_ids = [sample.id for sample in samples]
    
    # Get sample submitted data
    if sample_ids:
        sample_submitted_records = db.query(SampleSubmitted).filter(SampleSubmitted.sample_id.in_(sample_ids)).all()
        for record in sample_submitted_records:
            # Find the corresponding sample to get the bpa_sample_id
            sample = next((s for s in samples if s.id == record.sample_id), None)
            bpa_sample_id = sample.bpa_sample_id if sample else None
            
            response.samples.append(SampleSubmittedJson(
                sample_id=record.sample_id,
                bpa_sample_id=bpa_sample_id,
                submitted_json=record.submitted_json,
                status=record.status
            ))
    
    # Get experiments for these samples
    if sample_ids:
        experiments = db.query(Experiment).filter(Experiment.sample_id.in_(sample_ids)).all()
        experiment_ids = [experiment.id for experiment in experiments]
        
        # Get experiment submitted data
        if experiment_ids:
            experiment_submitted_records = db.query(ExperimentSubmitted).filter(ExperimentSubmitted.experiment_id.in_(experiment_ids)).all()
            for record in experiment_submitted_records:
                # Find the corresponding experiment to get the bpa_package_id
                experiment = next((e for e in experiments if e.id == record.experiment_id), None)
                bpa_package_id = experiment.bpa_package_id if experiment else None
                
                response.experiments.append(ExperimentSubmittedJson(
                    experiment_id=record.experiment_id,
                    bpa_package_id=bpa_package_id,
                    submitted_json=record.submitted_json,
                    status=record.status
                ))
            
            # Get reads for these experiments
            reads = db.query(Read).filter(Read.experiment_id.in_(experiment_ids)).all()
            for read in reads:
                if read.submitted_json:  # Only include reads that have submitted_json
                    response.reads.append(ReadSubmittedJson(
                        read_id=read.id,
                        experiment_id=read.experiment_id,
                        file_name=read.file_name,
                        submitted_json=read.submitted_json,
                        status=read.status
                    ))
    
    return response


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


@router.post("/bulk-import", response_model=BulkImportResponse)
def bulk_import_organisms(
    *,
    db: Session = Depends(get_db),
    organisms_data: Dict[str, Dict[str, Any]],  # Accept direct dictionary format from unique_organisms.json
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Bulk import organisms from a dictionary keyed by organism_grouping_key.
    
    The request body should directly match the format of the JSON file in data/unique_organisms.json,
    which is a dictionary keyed by organism_grouping_key without a wrapping 'organisms' key.
    """
    # Only users with 'curator' or 'admin' role can import organisms
    require_role(current_user, ["curator", "admin"])
    
    created_count = 0
    skipped_count = 0
    
    for organism_grouping_key, organism_data in organisms_data.items():
        # Extract tax_id from the organism data
        if "taxon_id" in organism_data:
            tax_id = organism_data["taxon_id"]
        else:
            print(f"Missing taxon_id for organism: {organism_data}")
            skipped_count += 1
            continue
        
        if "organism_grouping_key" not in organism_data:
            print(f"Missing organism_grouping_key for organism: {organism_data}")
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
