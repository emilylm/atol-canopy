"""
XML export endpoints for ENA run submissions.

This module provides endpoints to generate XML files for ENA run submissions
from the internal database records.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user, get_db
from app.models.read import Read
from app.models.user import User
from app.utils.xml_generator import generate_run_xml, generate_runs_xml

router = APIRouter()


@router.get("/reads/{read_id}/xml", response_class=PlainTextResponse)
def get_read_xml(
    *,
    db: Session = Depends(get_db),
    read_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Generate ENA run XML for a specific read.
    
    Returns the XML representation of the read submission data.
    """
    # Find the read record
    read = db.query(Read).filter(Read.id == read_id).first()
    
    if not read:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Read not found",
        )
    
    if not read.submission_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Read has no submission_json data",
        )
    
    # Generate XML using the utility function
    xml_content = generate_run_xml(
        submission_json=read.submission_json,
        alias=read.bpa_dataset_id if read.bpa_dataset_id else f"read_{read_id}",
        accession=read.submission_json.get("run_accession")
    )
    
    return xml_content


@router.get("/reads/xml", response_class=PlainTextResponse)
def get_reads_xml(
    *,
    db: Session = Depends(get_db),
    read_ids: List[UUID] = Query(None, description="List of read IDs to include in the XML"),
    experiment_id: Optional[UUID] = Query(None, description="Filter by experiment ID"),
    status: Optional[str] = Query(None, description="Filter by submission status"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Generate ENA run XML for multiple reads.
    
    Returns the XML representation of the read submission data for all specified reads.
    If no read_ids are provided, all reads matching the filters are included.
    """
    # Build the query
    query = db.query(Read)
    
    # Apply filters if provided
    if read_ids:
        query = query.filter(Read.id.in_(read_ids))
    
    if experiment_id:
        query = query.filter(Read.experiment_id == experiment_id)
    
    if status:
        query = query.filter(Read.status == status)
    
    # Get the reads
    reads = query.all()
    
    if not reads:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No read data found matching the criteria",
        )
    
    # Prepare the data for XML generation
    reads_data = []
    for read in reads:
        if not read.submission_json:
            continue
            
        # Get the run accession if available
        accession = read.submission_json.get("run_accession")
            
        # Use the BPA dataset ID as the alias if available
        alias = read.bpa_dataset_id if read.bpa_dataset_id else f"read_{read.id}"
            
        reads_data.append({
            "submission_json": read.submission_json,
            "alias": alias,
            "accession": accession
        })
    
    if not reads_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="None of the selected reads have submission_json data",
        )
    
    # Generate XML using the utility function
    xml_content = generate_runs_xml(reads_data)
    
    return xml_content


@router.get("/experiments/{experiment_id}/reads/xml", response_class=PlainTextResponse)
def get_experiment_reads_xml(
    *,
    db: Session = Depends(get_db),
    experiment_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Generate ENA run XML for reads associated with a specific experiment.
    
    Returns the XML representation of all read submission data associated with the experiment.
    """
    # Find the reads for this experiment
    reads = db.query(Read).filter(Read.experiment_id == experiment_id).all()
    
    if not reads:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No reads found for experiment with ID {experiment_id}"
        )
    
    # Prepare the data for XML generation
    reads_data = []
    for read in reads:
        if not read.submission_json:
            continue
            
        # Get the run accession if available
        accession = read.submission_json.get("run_accession")
            
        # Use the BPA dataset ID as the alias if available
        alias = read.bpa_dataset_id if read.bpa_dataset_id else f"read_{read.id}"
            
        reads_data.append({
            "submission_json": read.submission_json,
            "alias": alias,
            "accession": accession
        })
    
    if not reads_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="None of the reads for this experiment have submission_json data",
        )
    
    # Generate XML using the utility function
    xml_content = generate_runs_xml(reads_data)
    
    return xml_content
