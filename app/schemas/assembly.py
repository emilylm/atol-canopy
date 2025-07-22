from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Base Assembly schema
class AssemblyBase(BaseModel):
    """Base Assembly schema with common attributes."""
    assembly_id_serial: str
    organism_id: UUID
    sample_id: UUID
    experiment_id: Optional[UUID] = None
    assembly_accession_vector: Optional[str] = None
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
    assembly_accession_vector: Optional[str] = None
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


# Base AssemblySubmitted schema
class AssemblySubmittedBase(BaseModel):
    """Base AssemblySubmitted schema with common attributes."""
    assembly_id_serial: str
    organism_id: UUID
    sample_id: UUID
    experiment_id: Optional[UUID] = None
    status: str = Field(..., description="Status of the submission: draft, submitted, or rejected")


# Schema for creating a new assembly submission
class AssemblySubmittedCreate(AssemblySubmittedBase):
    """Schema for creating a new assembly submission."""
    assembly_id: Optional[UUID] = None
    submitted_json: Optional[Dict] = None
    submitted_at: Optional[datetime] = None


# Schema for updating an existing assembly submission
class AssemblySubmittedUpdate(BaseModel):
    """Schema for updating an existing assembly submission."""
    organism_id: Optional[UUID] = None
    sample_id: Optional[UUID] = None
    experiment_id: Optional[UUID] = None
    submitted_json: Optional[Dict] = None
    status: Optional[str] = None
    submitted_at: Optional[datetime] = None


# Schema for assembly submission in DB
class AssemblySubmittedInDBBase(AssemblySubmittedBase):
    """Base schema for AssemblySubmitted in DB, includes id and timestamps."""
    id: UUID
    assembly_id: Optional[UUID] = None
    submitted_json: Optional[Dict] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning assembly submission information
class AssemblySubmitted(AssemblySubmittedInDBBase):
    """Schema for returning assembly submission information."""
    pass


# Base AssemblyFetched schema
class AssemblyFetchedBase(BaseModel):
    """Base AssemblyFetched schema with common attributes."""
    assembly_id_serial: str
    assembly_accession_vector: str
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
