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
from app.models.sample import SampleSubmission
from app.models.experiment import ExperimentSubmission
from app.models.user import User
from app.utils.xml_generator import generate_sample_xml, generate_experiment_xml
from app.models.organism import Organism

router = APIRouter()


@router.get("/samples/{sample_id}", response_class=PlainTextResponse)
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
    # Find the submission record for this sample
    sample_submission = db.query(SampleSubmission).filter(
        SampleSubmission.sample_id == sample_id
    ).first()
    
    if not sample_submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample submission data not found",
        )
    
    if not sample_submission.submission_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sample has no submission_json data",
        )
        
    # Get the organism data
    organism_id = sample_submission.organism_id
    if not organism_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sample_submitted object missing organism_id",
        )
        
    organism = db.query(Organism).filter(Organism.id == organism_id).first()
    
    if not organism:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organism with id {organism_id} not found",
        )
    
    # Generate XML using the utility function
    xml_content = generate_sample_xml(
        organism=organism,
        submission_json=sample_submission.submission_json,
        alias=sample_submission.sample.bpa_sample_id if sample_submission.sample else f"sample_{sample_submission.sample_id}",
        accession=sample_submission.sample.sample_accession if sample_submission.sample and sample_submission.sample.sample_accession else None
    )
    
    return xml_content

@router.get("/experiments/package/{bpa_package_id}", response_class=PlainTextResponse)
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
    
    # Find the submission records for this sample
    sample_submission = db.query(SampleSubmission).filter(
        SampleSubmission.sample_id == experiment.sample_id
    ).first()
    
    if not sample_submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No submission sample records found for experiment with bpa_package_id {bpa_package_id}"
        )
    
    if not sample_submission.submission_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sample has no submission_json data",
        )
    
    # Get the organism data
    organism_id = sample_submission.organism_id
    if not organism_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sample_submitted object missing organism_id",
        )
        
    organism = db.query(Organism).filter(Organism.id == organism_id).first()
    
    if not organism:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organism with id {organism_id} not found",
        )
    
    # Generate XML using the utility function
    xml_content = generate_sample_xml(
        organism=organism,
        submission_json=sample_submission.submission_json,
        alias=sample_submission.sample.bpa_sample_id if sample_submission.sample else f"sample_{sample_submission.sample_id}",
        accession=sample_submission.sample.sample_accession if sample_submission.sample and sample_submission.sample.sample_accession else None
    )
    
    return xml_content
