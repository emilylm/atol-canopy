"""
XML export endpoints for ENA submissions.

This module provides endpoints to generate XML files for various ENA submission types
(samples, experiments, runs, etc.) from the internal database records.
"""
import os
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_db, require_role
from app.models.sample import SampleSubmitted
from app.models.user import User
from app.utils.xml_generator import generate_sample_xml, generate_samples_xml

router = APIRouter()


@router.get("/samples/{sample_id}/xml", response_class=PlainTextResponse)
def get_sample_xml(
    *,
    db: Session = Depends(get_db),
    sample_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Generate ENA sample XML for a specific sample.
    
    Returns the XML representation of the sample submission data.
    """
    # Find the submitted record for this sample
    sample_submitted = db.query(SampleSubmitted).filter(
        SampleSubmitted.sample_id == sample_id
    ).first()
    
    if not sample_submitted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample submitted data not found",
        )
    
    if not sample_submitted.submitted_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sample has no submitted_json data",
        )
    
    # Generate XML using the utility function
    xml_content = generate_sample_xml(
        submitted_json=sample_submitted.submitted_json,
        alias=f"sample_{sample_id}",  # You might want to use a more meaningful alias
        accession=sample_submitted.sample.sample_accession if sample_submitted.sample and sample_submitted.sample.sample_accession else None
    )
    
    return xml_content


@router.get("/samples/xml", response_class=PlainTextResponse)
def get_samples_xml(
    *,
    db: Session = Depends(get_db),
    sample_ids: List[UUID] = Query(None, description="List of sample IDs to include in the XML"),
    status: Optional[str] = Query(None, description="Filter by submission status"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Generate ENA sample XML for multiple samples.
    
    Returns the XML representation of the sample submission data for all specified samples.
    If no sample_ids are provided, all samples with the specified status are included.
    """
    # Build the query
    query = db.query(SampleSubmitted)
    
    # Apply filters if provided
    if sample_ids:
        query = query.filter(SampleSubmitted.sample_id.in_(sample_ids))
    
    if status:
        query = query.filter(SampleSubmitted.status == status)
    
    # Get the samples
    samples = query.all()
    
    if not samples:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No sample submitted data found matching the criteria",
        )
    
    # Prepare the data for XML generation
    samples_data = []
    for sample in samples:
        if not sample.submitted_json:
            continue
            
        # Get the sample accession if available
        accession = None
        if sample.sample and sample.sample.sample_accession:
            accession = sample.sample.sample_accession
            
        # Use the BPA sample ID as the alias if available
        alias = f"sample_{sample.sample_id}"
        if sample.sample and sample.sample.bpa_sample_id:
            alias = sample.sample.bpa_sample_id
            
        samples_data.append({
            "submitted_json": sample.submitted_json,
            "alias": alias,
            "accession": accession
        })
    
    if not samples_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="None of the selected samples have submitted_json data",
        )
    
    # Generate XML using the utility function
    xml_content = generate_samples_xml(samples_data)
    
    return xml_content


@router.get("/experiments/package/{bpa_package_id}/samples/xml", response_class=PlainTextResponse)
def get_experiment_samples_xml(
    *,
    db: Session = Depends(get_db),
    bpa_package_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Generate ENA sample XML for samples associated with a specific experiment package.
    
    Returns the XML representation of all sample submission data associated with the experiment.
    """
    # Find the experiment with the given bpa_package_id
    from app.models.experiment import Experiment
    
    experiment = db.query(Experiment).filter(Experiment.bpa_package_id == bpa_package_id).first()
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with bpa_package_id {bpa_package_id} not found"
        )
    
    # Get the sample_id from the experiment
    if not experiment.sample_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with bpa_package_id {bpa_package_id} has no associated sample"
        )
    
    # Find the submitted records for this sample
    sample_submitted = db.query(SampleSubmitted).filter(
        SampleSubmitted.sample_id == experiment.sample_id
    ).first()
    
    if not sample_submitted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No submitted sample records found for experiment with bpa_package_id {bpa_package_id}"
        )
    
    if not sample_submitted.submitted_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sample has no submitted_json data",
        )
    
    # Generate XML using the utility function
    xml_content = generate_sample_xml(
        submitted_json=sample_submitted.submitted_json,
        alias=sample_submitted.sample.bpa_sample_id if sample_submitted.sample else f"sample_{sample_submitted.sample_id}",
        accession=sample_submitted.sample.sample_accession if sample_submitted.sample and sample_submitted.sample.sample_accession else None
    )
    
    return xml_content
