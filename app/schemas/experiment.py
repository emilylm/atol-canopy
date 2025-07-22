from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Base Experiment schema
class ExperimentBase(BaseModel):
    """Base Experiment schema with common attributes."""
    experiment_id_serial: str
    sample_id: UUID
    experiment_accession_vector: str
    run_accession_text: UUID
    internal_notes: Optional[str] = None
    internal_priority_flag: Optional[str] = None


# Schema for creating a new experiment
class ExperimentCreate(ExperimentBase):
    """Schema for creating a new experiment."""
    source_json: Optional[Dict] = None


# Schema for updating an existing experiment
class ExperimentUpdate(BaseModel):
    """Schema for updating an existing experiment."""
    sample_id: Optional[UUID] = None
    experiment_accession_vector: Optional[str] = None
    run_accession_text: Optional[UUID] = None
    source_json: Optional[Dict] = None
    internal_notes: Optional[str] = None
    internal_priority_flag: Optional[str] = None


# Schema for experiment in DB
class ExperimentInDBBase(ExperimentBase):
    """Base schema for Experiment in DB, includes id and timestamps."""
    id: UUID
    source_json: Optional[Dict] = None
    synced_at: Optional[datetime] = None
    last_checked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning experiment information
class Experiment(ExperimentInDBBase):
    """Schema for returning experiment information."""
    pass


# Base ExperimentSubmitted schema
class ExperimentSubmittedBase(BaseModel):
    """Base ExperimentSubmitted schema with common attributes."""
    experiment_id_serial: str
    sample_id: UUID
    status: str = Field(..., description="Status of the submission: draft, submitted, or rejected")


# Schema for creating a new experiment submission
class ExperimentSubmittedCreate(ExperimentSubmittedBase):
    """Schema for creating a new experiment submission."""
    experiment_id: Optional[UUID] = None
    experiment_accession_vector: Optional[str] = None
    run_accession_text: Optional[UUID] = None
    submitted_json: Optional[Dict] = None
    submitted_at: Optional[datetime] = None


# Schema for updating an existing experiment submission
class ExperimentSubmittedUpdate(BaseModel):
    """Schema for updating an existing experiment submission."""
    sample_id: Optional[UUID] = None
    experiment_accession_vector: Optional[str] = None
    run_accession_text: Optional[UUID] = None
    submitted_json: Optional[Dict] = None
    status: Optional[str] = None
    submitted_at: Optional[datetime] = None


# Schema for experiment submission in DB
class ExperimentSubmittedInDBBase(ExperimentSubmittedBase):
    """Base schema for ExperimentSubmitted in DB, includes id and timestamps."""
    id: UUID
    experiment_id: Optional[UUID] = None
    experiment_accession_vector: Optional[str] = None
    run_accession_text: Optional[UUID] = None
    submitted_json: Optional[Dict] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning experiment submission information
class ExperimentSubmitted(ExperimentSubmittedInDBBase):
    """Schema for returning experiment submission information."""
    pass


# Base ExperimentFetched schema
class ExperimentFetchedBase(BaseModel):
    """Base ExperimentFetched schema with common attributes."""
    experiment_id_serial: str
    experiment_accession_vector: str
    run_accession_text: UUID
    sample_id: UUID
    fetched_at: datetime


# Schema for creating a new experiment fetch record
class ExperimentFetchedCreate(ExperimentFetchedBase):
    """Schema for creating a new experiment fetch record."""
    experiment_id: Optional[UUID] = None
    raw_json: Optional[Dict] = None


# Schema for experiment fetch record in DB
class ExperimentFetchedInDBBase(ExperimentFetchedBase):
    """Base schema for ExperimentFetched in DB, includes id and timestamps."""
    id: UUID
    experiment_id: Optional[UUID] = None
    raw_json: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning experiment fetch record information
class ExperimentFetched(ExperimentFetchedInDBBase):
    """Schema for returning experiment fetch record information."""
    pass
