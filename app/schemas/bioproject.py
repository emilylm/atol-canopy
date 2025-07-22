from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


# Base Bioproject schema
class BioprojectBase(BaseModel):
    """Base Bioproject schema with common attributes."""
    bioproject_accession: str
    alias: str
    alias_md5: str
    study_name: str
    new_study_type: Optional[str] = None
    study_abstract: Optional[str] = None


# Schema for creating a new Bioproject
class BioprojectCreate(BioprojectBase):
    """Schema for creating a new Bioproject."""
    pass


# Schema for updating an existing Bioproject
class BioprojectUpdate(BaseModel):
    """Schema for updating an existing Bioproject."""
    alias: Optional[str] = None
    alias_md5: Optional[str] = None
    study_name: Optional[str] = None
    new_study_type: Optional[str] = None
    study_abstract: Optional[str] = None


# Schema for Bioproject in DB
class BioprojectInDBBase(BioprojectBase):
    """Base schema for Bioproject in DB, includes id and timestamps."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning Bioproject information
class Bioproject(BioprojectInDBBase):
    """Schema for returning Bioproject information."""
    pass


# Base BioprojectExperiment schema
class BioprojectExperimentBase(BaseModel):
    """Base BioprojectExperiment schema with common attributes."""
    bioproject_id: UUID
    experiment_id: UUID
    bioproject_accession: str


# Schema for creating a new BioprojectExperiment
class BioprojectExperimentCreate(BioprojectExperimentBase):
    """Schema for creating a new BioprojectExperiment."""
    pass


# Schema for BioprojectExperiment in DB
class BioprojectExperimentInDBBase(BioprojectExperimentBase):
    """Base schema for BioprojectExperiment in DB, includes id and timestamps."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for returning BioprojectExperiment information
class BioprojectExperiment(BioprojectExperimentInDBBase):
    """Schema for returning BioprojectExperiment information."""
    pass
