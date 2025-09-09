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
from app.models.experiment import Experiment, ExperimentSubmission
from app.models.read import Read
from app.models.user import User
from app.utils.xml_generator import generate_experiment_xml, generate_runs_xml

router = APIRouter()


@router.get("/experiments/{experiment_id}", response_class=PlainTextResponse)
def get_experiment_xml(
    *,
    db: Session = Depends(get_db),
    experiment_id: UUID,
    study_accession: Optional[str] = Query(None, description="Study accession to use in the XML"),
    study_alias: Optional[str] = Query(None, description="Study refname to use in the XML"),
    sample_accession: Optional[str] = Query(None, description="Sample accession to use in the XML"),
    sample_alias: Optional[str] = Query(None, description="Sample refname to use in the XML"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Generate ENA experiment XML for a specific experiment.
    
    Returns the XML representation of the experiment submission data.
    """
    # Find the submission record for this experiment
    experiment_submission = db.query(ExperimentSubmission).filter(
        ExperimentSubmission.experiment_id == experiment_id
    ).first()
    
    if not experiment_submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment submission data not found",
        )
    
    if not experiment_submission.submission_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Experiment has no submission_json data",
        )
    
    # Generate XML using the utility function
    xml_content = generate_experiment_xml(
        submission_json=experiment_submission.submission_json,
        alias=experiment_submission.submission_json.get("alias"),
        study_accession=study_accession,
        study_alias=study_alias,
        sample_accession=sample_accession,
        sample_alias=sample_alias,
        accession=experiment_submission.experiment_accession if experiment_submission.experiment_accession else None
    )
    
    return xml_content


@router.get("/experiments/package/{bpa_package_id}", response_class=PlainTextResponse)
def get_experiment_by_package_id_xml(
    *,
    db: Session = Depends(get_db),
    bpa_package_id: str,
    study_accession: Optional[str] = Query(None, description="Study accession to use in the XML"),
    study_alias: Optional[str] = Query(None, description="Study refname to use in the XML"),
    sample_accession: Optional[str] = Query(None, description="Sample accession to use in the XML"),
    sample_alias: Optional[str] = Query(None, description="Sample refname to use in the XML"),
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
    
    # Find the submission records for this experiment
    experiment_submission = db.query(ExperimentSubmission).filter(
        ExperimentSubmission.experiment_id == experiment.id
    ).first()
    
    if not experiment_submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No submission experiment records found for experiment with bpa_package_id {bpa_package_id}"
        )
    
    if not experiment_submission.submission_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Experiment has no submission_json data",
        )
    
    # Generate XML using the utility function
    xml_content = generate_experiment_xml(
        submission_json=experiment_submission.submission_json,
        alias=experiment_submission.submission_json.get("alias"),
        study_accession=study_accession,
        study_alias=study_alias,
        sample_accession=sample_accession,
        sample_alias=sample_alias,
        accession=experiment_submission.experiment_accession if experiment_submission.experiment_accession else None
    )
    
    return xml_content
