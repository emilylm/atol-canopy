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
    sample_name: Optional[str] = None
    internal_notes: Optional[str] = None
    internal_priority_flag: Optional[str] = None


# Schema for creating a new sample
class SampleCreate(SampleBase):
    """Schema for creating a new sample."""
    source_json: Optional[Dict] = None


# Schema for updating an existing sample
class SampleUpdate(BaseModel):
    """Schema for updating an existing sample."""
    organism_id: Optional[UUID] = None
    sample_accession: Optional[str] = None
    sample_name: Optional[str] = None
    source_json: Optional[Dict] = None
    internal_notes: Optional[str] = None
    internal_priority_flag: Optional[str] = None


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


# Base SampleSubmitted schema
class SampleSubmittedBase(BaseModel):
    """Base SampleSubmitted schema with common attributes."""
    organism_id: Optional[UUID] = None
    status: SubmissionStatus = Field(default=SubmissionStatus.DRAFT, description="Status of the submission")


# Schema for creating a new sample submission
class SampleSubmittedCreate(SampleSubmittedBase):
    """Schema for creating a new sample submission."""
    sample_id: Optional[UUID] = None
    internal_json: Optional[Dict] = None
    submitted_json: Optional[Dict] = None
    submitted_at: Optional[datetime] = None


# Schema for updating an existing sample submission
class SampleSubmittedUpdate(BaseModel):
    """Schema for updating an existing sample submission."""
    organism_id: Optional[UUID] = None
    internal_json: Optional[Dict] = None
    submitted_json: Optional[Dict] = None
    status: Optional[SubmissionStatus] = None
    submitted_at: Optional[datetime] = None


# Schema for sample submission in DB
class SampleSubmittedInDBBase(SampleSubmittedBase):
    """Base schema for SampleSubmitted in DB, includes id and timestamps."""
    id: UUID
    sample_id: Optional[UUID] = None
    internal_json: Optional[Dict] = None
    submitted_json: Optional[Dict] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning sample submission information
class SampleSubmitted(SampleSubmittedInDBBase):
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
