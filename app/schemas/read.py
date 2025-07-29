from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


# Base Read schema
class ReadBase(BaseModel):
    """Base Read schema with common attributes."""
    experiment_id: UUID
    bpa_dataset_id: Optional[str] = None
    bpa_resource_id: Optional[str] = None
    file_name: Optional[str] = None
    file_format: Optional[str] = None
    file_size: Optional[int] = None
    file_submission_date: Optional[str] = None
    file_checksum: Optional[str] = None
    read_access_date: Optional[str] = None
    bioplatforms_url: Optional[str] = None


# Schema for creating a new Read
class ReadCreate(ReadBase):
    """Schema for creating a new Read."""
    pass


# Schema for updating an existing Read
class ReadUpdate(BaseModel):
    """Schema for updating an existing Read."""
    experiment_id: Optional[UUID] = None
    bpa_dataset_id: Optional[str] = None
    bpa_resource_id: Optional[str] = None
    file_name: Optional[str] = None
    file_format: Optional[str] = None
    file_size: Optional[int] = None
    file_submission_date: Optional[str] = None
    file_checksum: Optional[str] = None
    read_access_date: Optional[str] = None
    bioplatforms_url: Optional[str] = None


# Schema for Read in DB
class ReadInDBBase(ReadBase):
    """Base schema for Read in DB, includes id and timestamps."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning Read information
class Read(ReadInDBBase):
    """Schema for returning Read information."""
    pass
