from typing import Dict, Any, List, Optional
from uuid import UUID

from pydantic import BaseModel


class SampleSubmittedJson(BaseModel):
    """Schema for sample submitted_json data with sample ID"""
    sample_id: UUID
    bpa_sample_id: Optional[str] = None
    submitted_json: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ExperimentSubmittedJson(BaseModel):
    """Schema for experiment submitted_json data with experiment ID"""
    experiment_id: UUID
    bpa_package_id: Optional[str] = None
    submitted_json: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ReadSubmittedJson(BaseModel):
    """Schema for read submitted_json data with read ID"""
    read_id: UUID
    experiment_id: UUID
    file_name: Optional[str] = None
    submitted_json: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class OrganismSubmittedJsonResponse(BaseModel):
    """Schema for returning all submitted_json data related to an organism"""
    organism_id: UUID
    organism_grouping_key: str
    scientific_name: Optional[str] = None
    common_name: Optional[str] = None
    samples: List[SampleSubmittedJson] = []
    experiments: List[ExperimentSubmittedJson] = []
    reads: List[ReadSubmittedJson] = []
