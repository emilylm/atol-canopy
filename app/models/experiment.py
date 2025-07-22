import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Experiment(Base):
    """
    Experiment model for storing experiment information with 1:1 mapping to ENA runs.
    
    This model corresponds to the 'experiment' table in the database.
    """
    __tablename__ = "experiment"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id_serial = Column(String, unique=True, nullable=False)
    sample_id = Column(UUID(as_uuid=True), ForeignKey("sample.id"), nullable=False)
    experiment_accession_vector = Column(Text, unique=True, nullable=False)
    run_accession_text = Column(UUID(as_uuid=True), unique=True, nullable=False)
    source_json = Column(JSONB, nullable=True)
    internal_notes = Column(Text, nullable=True)
    internal_priority_flag = Column(Text, nullable=True)
    synced_at = Column(DateTime, nullable=True)
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sample = relationship("Sample", backref="experiments")


class ExperimentSubmitted(Base):
    """
    ExperimentSubmitted model for storing experiment data staged for submission to ENA.
    
    This model corresponds to the 'experiment_submitted' table in the database.
    """
    __tablename__ = "experiment_submitted"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiment.id"), nullable=True)
    experiment_id_serial = Column(String, nullable=False)
    experiment_accession_vector = Column(Text, nullable=True)
    run_accession_text = Column(UUID(as_uuid=True), nullable=True)
    sample_id = Column(UUID(as_uuid=True), ForeignKey("sample.id"), nullable=False)
    submitted_json = Column(JSONB, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    experiment = relationship("Experiment", backref="submitted_records")
    sample = relationship("Sample")


class ExperimentFetched(Base):
    """
    ExperimentFetched model for storing immutable history of experiment data from ENA.
    
    This model corresponds to the 'experiment_fetched' table in the database.
    """
    __tablename__ = "experiment_fetched"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiment.id"), nullable=True)
    experiment_id_serial = Column(String, nullable=False)
    experiment_accession_vector = Column(Text, nullable=False)
    run_accession_text = Column(UUID(as_uuid=True), nullable=False)
    sample_id = Column(UUID(as_uuid=True), ForeignKey("sample.id"), nullable=False)
    raw_json = Column(JSONB, nullable=True)
    fetched_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    experiment = relationship("Experiment", backref="fetched_records")
    sample = relationship("Sample")
