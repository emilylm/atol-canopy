import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
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
    assembly_id_serial = Column(String, unique=True, nullable=False)
    organism_id = Column(UUID(as_uuid=True), ForeignKey("organism.id"), nullable=False)
    sample_id = Column(UUID(as_uuid=True), ForeignKey("sample.id"), nullable=False)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiment.id"), nullable=True)
    assembly_accession_vector = Column(Text, unique=True, nullable=True)
    source_json = Column(JSONB, nullable=True)
    internal_notes = Column(Text, nullable=True)
    synced_at = Column(DateTime, nullable=True)
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organism = relationship("Organism", backref="assemblies")
    sample = relationship("Sample", backref="assemblies")
    experiment = relationship("Experiment", backref="assemblies")


class AssemblySubmitted(Base):
    """
    AssemblySubmitted model for storing assembly data staged for submission to ENA.
    
    This model corresponds to the 'assembly_submitted' table in the database.
    """
    __tablename__ = "assembly_submitted"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assembly_id = Column(UUID(as_uuid=True), ForeignKey("assembly.id"), nullable=True)
    assembly_id_serial = Column(String, nullable=False)
    organism_id = Column(UUID(as_uuid=True), ForeignKey("organism.id"), nullable=False)
    sample_id = Column(UUID(as_uuid=True), ForeignKey("sample.id"), nullable=False)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiment.id"), nullable=True)
    submitted_json = Column(JSONB, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assembly = relationship("Assembly", backref="submitted_records")
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
    assembly_id_serial = Column(String, nullable=False)
    assembly_accession_vector = Column(Text, nullable=False)
    organism_id = Column(UUID(as_uuid=True), ForeignKey("organism.id"), nullable=False)
    sample_id = Column(UUID(as_uuid=True), ForeignKey("sample.id"), nullable=False)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiment.id"), nullable=True)
    fetched_json = Column(JSONB, nullable=True)
    fetched_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assembly = relationship("Assembly", backref="fetched_records")
    organism = relationship("Organism")
    sample = relationship("Sample")
    experiment = relationship("Experiment")
