import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Assembly(Base):
    """
    Assembly model for storing genomic assembly information.
    
    This model corresponds to the 'assembly' table in the database.
    """
    __tablename__ = "assembly"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organism_id = Column(UUID(as_uuid=True), ForeignKey("organism.id"), nullable=False)
    sample_id = Column(UUID(as_uuid=True), ForeignKey("sample.id"), nullable=False)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiment.id"), nullable=True)
    assembly_accession = Column(Text, unique=True, nullable=True)
    source_json = Column(JSONB, nullable=True)
    internal_notes = Column(Text, nullable=True)
    synced_at = Column(DateTime, nullable=True)
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    organism = relationship("Organism", backref="assemblies")
    sample = relationship("Sample", backref="assemblies")
    experiment = relationship("Experiment", backref="assemblies")


class AssemblySubmission(Base):
    """
    AssemblySubmission model for storing assembly data staged for submission to ENA.
    
    This model corresponds to the 'assembly_submission' table in the database.
    """
    __tablename__ = "assembly_submission"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assembly_id = Column(UUID(as_uuid=True), ForeignKey("assembly.id"), nullable=True)
    organism_id = Column(UUID(as_uuid=True), ForeignKey("organism.id"), nullable=False)
    sample_id = Column(UUID(as_uuid=True), ForeignKey("sample.id"), nullable=False)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiment.id"), nullable=True)
    internal_json = Column(JSONB, nullable=True)
    submission_json = Column(JSONB, nullable=True)
    submission_at = Column(DateTime, nullable=True)
    status = Column(SQLAlchemyEnum("draft", "ready", "submission", "rejected", name="submission_status"), nullable=False, default="draft")
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    assembly = relationship("Assembly", backref="submission_records")
    organism = relationship("Organism")
    sample = relationship("Sample")
    experiment = relationship("Experiment")


class AssemblyFetched(Base):
    """
    AssemblyFetched model for storing immutable history of assembly data from ENA.
    
    This model corresponds to the 'assembly_fetched' table in the database.
    """
    __tablename__ = "assembly_fetched"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assembly_id = Column(UUID(as_uuid=True), ForeignKey("assembly.id"), nullable=True)
    assembly_accession = Column(Text, nullable=False)
    organism_id = Column(UUID(as_uuid=True), ForeignKey("organism.id"), nullable=False)
    sample_id = Column(UUID(as_uuid=True), ForeignKey("sample.id"), nullable=False)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiment.id"), nullable=True)
    fetched_json = Column(JSONB, nullable=True)
    fetched_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    assembly = relationship("Assembly", backref="fetched_records")
    organism = relationship("Organism")
    sample = relationship("Sample")
    experiment = relationship("Experiment")
