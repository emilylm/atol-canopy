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
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tax_id = Column(Integer, unique=True, nullable=False)
    scientific_name = Column(Text, nullable=False)
    common_name = Column(Text, nullable=True)
    taxonomy_lineage_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class OrganismSubmitted(Base):
    """
    OrganismSubmitted model for storing organism data staged for submission to ENA.
    
    This model corresponds to the 'organism_submitted' table in the database.
    """
    __tablename__ = "organism_submitted"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organism_id = Column(UUID(as_uuid=True), nullable=True)
    tax_id = Column(Integer, nullable=False)
    scientific_name = Column(Text, nullable=False)
    common_name = Column(Text, nullable=True)
    taxonomy_lineage_json = Column(JSONB, nullable=True)
    internal_json = Column(JSONB, nullable=True)
    submitted_json = Column(JSONB, nullable=True)
    status = Column(SQLAlchemyEnum("draft", "ready", "submitted", "rejected", name="submission_status"), nullable=False, default="draft")
    submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class OrganismFetched(Base):
    """
    OrganismFetched model for storing immutable history of organism data from ENA.
    
    This model corresponds to the 'organism_fetched' table in the database.
    """
    __tablename__ = "organism_fetched"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organism_id = Column(UUID(as_uuid=True), nullable=True)
    tax_id = Column(Integer, nullable=False)
    scientific_name = Column(Text, nullable=False)
    common_name = Column(Text, nullable=True)
    taxonomy_lineage_json = Column(JSONB, nullable=True)
    fetched_json = Column(JSONB, nullable=True)
    fetched_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
