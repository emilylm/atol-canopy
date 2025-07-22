from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


# Base Read schema
class ReadBase(BaseModel):
    """Base Read schema with common attributes."""
    read_id_serial: str
    experiment_id: UUID
    dataset_name_vector: str
    file_name: Optional[str] = None
    file_format: Optional[str] = None
    file_size: Optional[int] = None
    file_extension_date: Optional[str] = None
    file_md5: Optional[str] = None
    read_access_date: Optional[datetime] = None
    parameters_url: Optional[str] = None


# Schema for creating a new Read
class ReadCreate(ReadBase):
    """Schema for creating a new Read."""
    pass


# Schema for updating an existing Read
class ReadUpdate(BaseModel):
    """Schema for updating an existing Read."""
    experiment_id: Optional[UUID] = None
    dataset_name_vector: Optional[str] = None
    file_name: Optional[str] = None
    file_format: Optional[str] = None
    file_size: Optional[int] = None
    file_extension_date: Optional[str] = None
    file_md5: Optional[str] = None
    read_access_date: Optional[datetime] = None
    parameters_url: Optional[str] = None


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
