from datetime import datetime
from enum import Enum
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Enum for submission status
class SubmissionStatus(str, Enum):
    DRAFT = 'draft'
    READY = 'ready'
    SUBMITTED = 'submitted'
    REJECTED = 'rejected'


# Base Organism schema
class OrganismBase(BaseModel):
    """Base Organism schema with common attributes."""
    tax_id: int
    scientific_name: str
    common_name: Optional[str] = None


# Schema for creating a new organism
class OrganismCreate(OrganismBase):
    """Schema for creating a new organism."""
    taxonomy_lineage_json: Optional[Dict] = None


# Schema for updating an existing organism
class OrganismUpdate(BaseModel):
    """Schema for updating an existing organism."""
    tax_id: Optional[int] = None
    scientific_name: Optional[str] = None
    common_name: Optional[str] = None
    taxonomy_lineage_json: Optional[Dict] = None


# Schema for organism in DB
class OrganismInDBBase(OrganismBase):
    """Base schema for Organism in DB, includes id and timestamps."""
    id: UUID
    taxonomy_lineage_json: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning organism information
class Organism(OrganismInDBBase):
    """Schema for returning organism information."""
    pass


# Base OrganismSubmitted schema
class OrganismSubmittedBase(BaseModel):
    """Base OrganismSubmitted schema with common attributes."""
    tax_id: int
    scientific_name: str
    common_name: Optional[str] = None
    status: SubmissionStatus = Field(..., description="Status of the submission")


# Schema for creating a new organism submission
class OrganismSubmittedCreate(OrganismSubmittedBase):
    """Schema for creating a new organism submission."""
    organism_id: Optional[UUID] = None
    taxonomy_lineage_json: Optional[Dict] = None
    submitted_json: Optional[Dict] = None
    submitted_at: Optional[datetime] = None


# Schema for updating an existing organism submission
class OrganismSubmittedUpdate(BaseModel):
    """Schema for updating an existing organism submission."""
    tax_id: Optional[int] = None
    scientific_name: Optional[str] = None
    common_name: Optional[str] = None
    taxonomy_lineage_json: Optional[Dict] = None
    submitted_json: Optional[Dict] = None
    status: Optional[SubmissionStatus] = None
    submitted_at: Optional[datetime] = None


# Schema for organism submission in DB
class OrganismSubmittedInDBBase(OrganismSubmittedBase):
    """Base schema for OrganismSubmitted in DB, includes id and timestamps."""
    id: UUID
    organism_id: Optional[UUID] = None
    taxonomy_lineage_json: Optional[Dict] = None
    submitted_json: Optional[Dict] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning organism submission information
class OrganismSubmitted(OrganismSubmittedInDBBase):
    """Schema for returning organism submission information."""
    pass


# Base OrganismFetched schema
class OrganismFetchedBase(BaseModel):
    """Base OrganismFetched schema with common attributes."""
    tax_id: int
    scientific_name: str
    common_name: Optional[str] = None
    fetched_at: datetime


# Schema for creating a new organism fetch record
class OrganismFetchedCreate(OrganismFetchedBase):
    """Schema for creating a new organism fetch record."""
    organism_id: Optional[UUID] = None
    taxonomy_lineage_json: Optional[Dict] = None
    fetched_json: Optional[Dict] = None


# Schema for organism fetch record in DB
class OrganismFetchedInDBBase(OrganismFetchedBase):
    """Base schema for OrganismFetched in DB, includes id and timestamps."""
    id: UUID
    organism_id: Optional[UUID] = None
    taxonomy_lineage_json: Optional[Dict] = None
    fetched_json: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning organism fetch record information
class OrganismFetched(OrganismFetchedInDBBase):
    """Schema for returning organism fetch record information."""
    pass
