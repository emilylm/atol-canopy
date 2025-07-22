from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Base Sample schema
class SampleBase(BaseModel):
    """Base Sample schema with common attributes."""
    sample_id_serial: str
    organism_id: Optional[UUID] = None
    sample_accession_vector: Optional[str] = None
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
    sample_accession_vector: Optional[str] = None
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
    sample_id_serial: str
    organism_id: Optional[UUID] = None
    status: str = Field(..., description="Status of the submission: draft, submitted, or rejected")


# Schema for creating a new sample submission
class SampleSubmittedCreate(SampleSubmittedBase):
    """Schema for creating a new sample submission."""
    sample_id: Optional[UUID] = None
    submitted_json: Optional[Dict] = None
    submitted_at: Optional[datetime] = None


# Schema for updating an existing sample submission
class SampleSubmittedUpdate(BaseModel):
    """Schema for updating an existing sample submission."""
    organism_id: Optional[UUID] = None
    submitted_json: Optional[Dict] = None
    status: Optional[str] = None
    submitted_at: Optional[datetime] = None


# Schema for sample submission in DB
class SampleSubmittedInDBBase(SampleSubmittedBase):
    """Base schema for SampleSubmitted in DB, includes id and timestamps."""
    id: UUID
    sample_id: Optional[UUID] = None
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
    sample_id_serial: str
    sample_accession_vector: str
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


# Base SampleRelationship schema
class SampleRelationshipBase(BaseModel):
    """Base SampleRelationship schema with common attributes."""
    source_sample_id: UUID
    target_sample_id: UUID
    relationship_type: str = Field(..., description="Type of relationship: derived_from, subsample_of, parent_of, child_of")


# Schema for creating a new sample relationship
class SampleRelationshipCreate(SampleRelationshipBase):
    """Schema for creating a new sample relationship."""
    pass


# Schema for updating an existing sample relationship
class SampleRelationshipUpdate(BaseModel):
    """Schema for updating an existing sample relationship."""
    relationship_type: Optional[str] = None


# Schema for sample relationship in DB
class SampleRelationshipInDBBase(SampleRelationshipBase):
    """Base schema for SampleRelationship in DB, includes id and timestamps."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning sample relationship information
class SampleRelationship(SampleRelationshipInDBBase):
    """Schema for returning sample relationship information."""
    pass
