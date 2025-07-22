import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
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
    sample_id_serial = Column(String, unique=True, nullable=False)
    organism_id = Column(UUID(as_uuid=True), ForeignKey("organism.id"), nullable=True)
    sample_accession_vector = Column(Text, unique=True, nullable=True)
    source_json = Column(JSONB, nullable=True)
    internal_notes = Column(Text, nullable=True)
    internal_priority_flag = Column(Text, nullable=True)
    synced_at = Column(DateTime, nullable=True)
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    sample_id_serial = Column(String, nullable=False)
    organism_id = Column(UUID(as_uuid=True), ForeignKey("organism.id"), nullable=True)
    submitted_json = Column(JSONB, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    sample_id_serial = Column(String, nullable=False)
    sample_accession_vector = Column(Text, nullable=False)
    organism_id = Column(UUID(as_uuid=True), ForeignKey("organism.id"), nullable=True)
    raw_json = Column(JSONB, nullable=True)
    fetched_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sample = relationship("Sample", backref="fetched_records")
    organism = relationship("Organism")


class SampleRelationship(Base):
    """
    SampleRelationship model for tracking relationships between samples.
    
    This model corresponds to the 'sample_relationship' table in the database.
    """
    __tablename__ = "sample_relationship"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_sample_id = Column(UUID(as_uuid=True), ForeignKey("sample.id"), nullable=False)
    target_sample_id = Column(UUID(as_uuid=True), ForeignKey("sample.id"), nullable=False)
    relationship_type = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source_sample = relationship("Sample", foreign_keys=[source_sample_id], backref="source_relationships")
    target_sample = relationship("Sample", foreign_keys=[target_sample_id], backref="target_relationships")
