from enum import Enum
# Enum for submission status
class SubmissionStatus(str, Enum):
    DRAFT = 'draft'
    READY = 'ready'
    SUBMITTED = 'submitted'
    REJECTED = 'rejected'