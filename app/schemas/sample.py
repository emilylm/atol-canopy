from datetime import datetime
from enum import Enum
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Enum for submission status
from app.schemas.common import SubmissionStatus

# Base Sample schema
class SampleBase(BaseModel):
    """Base Sample schema with common attributes."""
    organism_id: Optional[UUID] = None
    sample_accession: Optional[str] = None
    bpa_sample_id: Optional[str] = None

# Schema for creating a new sample
class SampleCreate(SampleBase):
    """Schema for creating a new sample."""
    source_json: Optional[Dict] = None


# Schema for updating an existing sample
class SampleUpdate(BaseModel):
    """Schema for updating an existing sample."""
    organism_id: Optional[UUID] = None
    sample_accession: Optional[str] = None
    bpa_sample_id: Optional[str] = None
    source_json: Optional[Dict] = None

# Schema for sample in DB
class SampleInDBBase(SampleBase):
    """Base schema for Sample in DB, includes id and timestamps."""
    id: UUID
    source_json: Optional[Dict] = None
    synced_at: Optional[datetime] = None
    last_checked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning sample information
class Sample(SampleInDBBase):
    """Schema for returning sample information."""
    pass


# Base SampleSubmission schema
class SampleSubmissionBase(BaseModel):
    """Base SampleSubmission schema with common attributes."""
    organism_id: Optional[UUID] = None
    status: SubmissionStatus = Field(default=SubmissionStatus.DRAFT, description="Status of the submission")


# Schema for creating a new sample submission
class SampleSubmissionCreate(SampleSubmissionBase):
    """Schema for creating a new sample submission."""
    sample_id: Optional[UUID] = None
    internal_json: Optional[Dict] = None
    submission_json: Optional[Dict] = None
    submission_at: Optional[datetime] = None


# Schema for updating an existing sample submission
class SampleSubmissionUpdate(BaseModel):
    """Schema for updating an existing sample submission."""
    organism_id: Optional[UUID] = None
    internal_json: Optional[Dict] = None
    submission_json: Optional[Dict] = None
    status: Optional[SubmissionStatus] = None
    submission_at: Optional[datetime] = None


# Schema for sample submission in DB
class SampleSubmissionInDBBase(SampleSubmissionBase):
    """Base schema for SampleSubmission in DB, includes id and timestamps."""
    id: UUID
    sample_id: Optional[UUID] = None
    internal_json: Optional[Dict] = None
    submission_json: Optional[Dict] = None
    submission_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning sample submission information
class SampleSubmission(SampleSubmissionInDBBase):
    """Schema for returning sample submission information."""
    pass


# Base SampleFetched schema
class SampleFetchedBase(BaseModel):
    """Base SampleFetched schema with common attributes."""
    sample_accession: str
    organism_id: Optional[UUID] = None
    fetched_at: datetime


# Schema for creating a new sample fetch record
class SampleFetchedCreate(SampleFetchedBase):
    """Schema for creating a new sample fetch record."""
    sample_id: Optional[UUID] = None
    raw_json: Optional[Dict] = None


# Schema for sample fetch record in DB
class SampleFetchedInDBBase(SampleFetchedBase):
    """Base schema for SampleFetched in DB, includes id and timestamps."""
    id: UUID
    sample_id: Optional[UUID] = None
    raw_json: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning sample fetch record information
class SampleFetched(SampleFetchedInDBBase):
    """Schema for returning sample fetch record information."""
    pass
