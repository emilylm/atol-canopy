from enum import Enum
from typing import Dict, Any, Optional

from pydantic import BaseModel

# Enum for submission status
class SubmissionStatus(str, Enum):
    DRAFT = 'draft'
    READY = 'ready'
    SUBMITTED = 'submission'
    REJECTED = 'rejected'


class SubmissionJsonResponse(BaseModel):
    """Schema for returning submission_json data"""
    submission_json: Optional[Dict[str, Any]] = None