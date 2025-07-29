from enum import Enum
from typing import Dict, Any, Optional

from pydantic import BaseModel

# Enum for submission status
class SubmissionStatus(str, Enum):
    DRAFT = 'draft'
    READY = 'ready'
    SUBMITTED = 'submitted'
    REJECTED = 'rejected'


class SubmittedJsonResponse(BaseModel):
    """Schema for returning submitted_json data"""
    submitted_json: Optional[Dict[str, Any]] = None