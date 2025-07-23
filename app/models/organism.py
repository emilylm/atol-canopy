import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.session import Base


# Enum for submission status
class SubmissionStatus(str):
    DRAFT = 'draft'
    READY = 'ready'
    SUBMITTED = 'submitted'
    REJECTED = 'rejected'


class Organism(Base):
    """
    Organism model for storing taxonomic information.
    
    This model corresponds to the 'organism' table in the database.
    """
    __tablename__ = "organism"
    
    tax_id = Column(Integer, unique=True, primary_key=True)
    scientific_name = Column(Text, nullable=False)
    common_name = Column(Text, nullable=True)
    common_name_source = Column(Text, nullable=True)
    bpa_json = Column(JSONB, nullable=True)
    taxonomy_lineage_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
