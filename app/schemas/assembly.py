from datetime import datetime
from enum import Enum
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import SubmissionStatus

# Base Assembly schema
class AssemblyBase(BaseModel):
    """Base Assembly schema with common attributes."""
    organism_id: UUID
    sample_id: UUID
    experiment_id: Optional[UUID] = None
    assembly_accession: Optional[str] = None
    internal_notes: Optional[str] = None


# Schema for creating a new assembly
class AssemblyCreate(AssemblyBase):
    """Schema for creating a new assembly."""
    source_json: Optional[Dict] = None


# Schema for updating an existing assembly
class AssemblyUpdate(BaseModel):
    """Schema for updating an existing assembly."""
    organism_id: Optional[UUID] = None
    sample_id: Optional[UUID] = None
    experiment_id: Optional[UUID] = None
    assembly_accession: Optional[str] = None
    source_json: Optional[Dict] = None
    internal_notes: Optional[str] = None


# Schema for assembly in DB
class AssemblyInDBBase(AssemblyBase):
    """Base schema for Assembly in DB, includes id and timestamps."""
    id: UUID
    source_json: Optional[Dict] = None
    synced_at: Optional[datetime] = None
    last_checked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning assembly information
class Assembly(AssemblyInDBBase):
    """Schema for returning assembly information."""
    pass


# Base AssemblySubmission schema
class AssemblySubmissionBase(BaseModel):
    """Base AssemblySubmission schema with common attributes."""
    organism_id: UUID
    sample_id: UUID
    experiment_id: Optional[UUID] = None
    status: SubmissionStatus = Field(default=SubmissionStatus.DRAFT, description="Status of the submission")


# Schema for creating a new assembly submission
class AssemblySubmissionCreate(AssemblySubmissionBase):
    """Schema for creating a new assembly submission."""
    assembly_id: Optional[UUID] = None
    internal_json: Optional[Dict] = None
    submission_json: Optional[Dict] = None
    submission_at: Optional[datetime] = None


# Schema for updating an existing assembly submission
class AssemblySubmissionUpdate(BaseModel):
    """Schema for updating an existing assembly submission."""
    organism_id: Optional[UUID] = None
    sample_id: Optional[UUID] = None
    experiment_id: Optional[UUID] = None
    internal_json: Optional[Dict] = None
    submission_json: Optional[Dict] = None
    status: Optional[SubmissionStatus] = None
    submission_at: Optional[datetime] = None


# Schema for assembly submission in DB
class AssemblySubmissionInDBBase(AssemblySubmissionBase):
    """Base schema for AssemblySubmission in DB, includes id and timestamps."""
    id: UUID
    assembly_id: Optional[UUID] = None
    internal_json: Optional[Dict] = None
    submission_json: Optional[Dict] = None
    submission_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning assembly submission information
class AssemblySubmission(AssemblySubmissionInDBBase):
    """Schema for returning assembly submission information."""
    pass


# Base AssemblyFetched schema
class AssemblyFetchedBase(BaseModel):
    """Base AssemblyFetched schema with common attributes."""
    assembly_accession: str
    organism_id: UUID
    sample_id: UUID
    experiment_id: Optional[UUID] = None
    fetched_at: datetime


# Schema for creating a new assembly fetch record
class AssemblyFetchedCreate(AssemblyFetchedBase):
    """Schema for creating a new assembly fetch record."""
    assembly_id: Optional[UUID] = None
    fetched_json: Optional[Dict] = None


# Schema for assembly fetch record in DB
class AssemblyFetchedInDBBase(AssemblyFetchedBase):
    """Base schema for AssemblyFetched in DB, includes id and timestamps."""
    id: UUID
    assembly_id: Optional[UUID] = None
    fetched_json: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning assembly fetch record information
class AssemblyFetched(AssemblyFetchedInDBBase):
    """Schema for returning assembly fetch record information."""
    pass
