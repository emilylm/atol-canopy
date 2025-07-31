"""
XML export endpoints for ENA experiment submissions.

This module provides endpoints to generate XML files for ENA experiment submissions
from the internal database records.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_db
from app.models.experiment import Experiment, ExperimentSubmitted
from app.models.user import User
from app.utils.xml_generator import generate_experiment_xml, generate_experiments_xml

router = APIRouter()


@router.get("/experiments/{experiment_id}/xml", response_class=PlainTextResponse)
def get_experiment_xml(
    *,
    db: Session = Depends(get_db),
    experiment_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Generate ENA experiment XML for a specific experiment.
    
    Returns the XML representation of the experiment submission data.
    """
    # Find the submitted record for this experiment
    experiment_submitted = db.query(ExperimentSubmitted).filter(
        ExperimentSubmitted.experiment_id == experiment_id
    ).first()
    
    if not experiment_submitted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment submitted data not found",
        )
    
    if not experiment_submitted.submitted_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Experiment has no submitted_json data",
        )
    
    # Generate XML using the utility function
    xml_content = generate_experiment_xml(
        submitted_json=experiment_submitted.submitted_json,
        alias=f"experiment_{experiment_id}",  # You might want to use a more meaningful alias
        accession=experiment_submitted.experiment_accession if experiment_submitted.experiment_accession else None
    )
    
    return xml_content


@router.get("/experiments/xml", response_class=PlainTextResponse)
def get_experiments_xml(
    *,
    db: Session = Depends(get_db),
    experiment_ids: List[UUID] = Query(None, description="List of experiment IDs to include in the XML"),
    status: Optional[str] = Query(None, description="Filter by submission status"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Generate ENA experiment XML for multiple experiments.
    
    Returns the XML representation of the experiment submission data for all specified experiments.
    If no experiment_ids are provided, all experiments with the specified status are included.
    """
    # Build the query
    query = db.query(ExperimentSubmitted)
    
    # Apply filters if provided
    if experiment_ids:
        query = query.filter(ExperimentSubmitted.experiment_id.in_(experiment_ids))
    
    if status:
        query = query.filter(ExperimentSubmitted.status == status)
    
    # Get the experiments
    experiments = query.all()
    
    if not experiments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No experiment submitted data found matching the criteria",
        )
    
    # Prepare the data for XML generation
    experiments_data = []
    for experiment in experiments:
        if not experiment.submitted_json:
            continue
            
        # Get the experiment accession if available
        accession = experiment.experiment_accession
            
        # Use the BPA package ID as the alias if available
        alias = f"experiment_{experiment.experiment_id}"
        if hasattr(experiment, 'experiment') and experiment.experiment and experiment.experiment.bpa_package_id:
            alias = experiment.experiment.bpa_package_id
            
        experiments_data.append({
            "submitted_json": experiment.submitted_json,
            "alias": alias,
            "accession": accession
        })
    
    if not experiments_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="None of the selected experiments have submitted_json data",
        )
    
    # Generate XML using the utility function
    xml_content = generate_experiments_xml(experiments_data)
    
    return xml_content


@router.get("/experiments/package/{bpa_package_id}/xml", response_class=PlainTextResponse)
def get_experiment_by_package_id_xml(
    *,
    db: Session = Depends(get_db),
    bpa_package_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Generate ENA experiment XML for a specific experiment package.
    
    Returns the XML representation of the experiment submission data associated with the package ID.
    """
    # Find the experiment with the given bpa_package_id
    experiment = db.query(Experiment).filter(Experiment.bpa_package_id == bpa_package_id).first()
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with bpa_package_id {bpa_package_id} not found"
        )
    
    # Find the submitted records for this experiment
    experiment_submitted = db.query(ExperimentSubmitted).filter(
        ExperimentSubmitted.experiment_id == experiment.id
    ).first()
    
    if not experiment_submitted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No submitted experiment records found for experiment with bpa_package_id {bpa_package_id}"
        )
    
    if not experiment_submitted.submitted_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Experiment has no submitted_json data",
        )
    
    # Generate XML using the utility function
    xml_content = generate_experiment_xml(
        submitted_json=experiment_submitted.submitted_json,
        alias=bpa_package_id,
        accession=experiment_submitted.experiment_accession
    )
    
    return xml_content
