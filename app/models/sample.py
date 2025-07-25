import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Sample(Base):
    """
    Sample model for storing biological sample information.
    
    This model corresponds to the 'sample' table in the database.
    """
    __tablename__ = "sample"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organism_id = Column(UUID(as_uuid=True), ForeignKey("organism.id"), nullable=True)
    sample_accession = Column(Text, unique=True, nullable=True)
    sample_name = Column(Text, unique=True, nullable=False)
    source_json = Column(JSONB, nullable=True)
    synced_at = Column(DateTime, nullable=True)
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    organism = relationship("Organism", backref="samples")


class SampleSubmitted(Base):
    """
    SampleSubmitted model for storing sample data staged for submission to ENA.
    
    This model corresponds to the 'sample_submitted' table in the database.
    """
    __tablename__ = "sample_submitted"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sample_id = Column(UUID(as_uuid=True), ForeignKey("sample.id"), nullable=True)
    organism_id = Column(UUID(as_uuid=True), ForeignKey("organism.id"), nullable=True)
    internal_json = Column(JSONB, nullable=True)
    submitted_json = Column(JSONB, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    status = Column(SQLAlchemyEnum("draft", "ready", "submitted", "rejected", name="submission_status"), nullable=False, default="draft")
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    sample = relationship("Sample", backref="submitted_records")
    organism = relationship("Organism")


class SampleFetched(Base):
    """
    SampleFetched model for storing immutable history of sample data from ENA.
    
    This model corresponds to the 'sample_fetched' table in the database.
    """
    __tablename__ = "sample_fetched"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sample_id = Column(UUID(as_uuid=True), ForeignKey("sample.id"), nullable=True)
    sample_accession = Column(Text, nullable=False)
    organism_id = Column(UUID(as_uuid=True), ForeignKey("organism.id"), nullable=True)
    raw_json = Column(JSONB, nullable=True)
    fetched_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    sample = relationship("Sample", backref="fetched_records")
    organism = relationship("Organism")

