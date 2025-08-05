import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Enum as SQLAlchemyEnum
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
    sample_id = Column(UUID(as_uuid=True), ForeignKey("sample.id"), nullable=True)
    experiment_accession = Column(Text, unique=True)
    run_accession = Column(Text, unique=True)
    bpa_package_id = Column(Text, unique=True)
    source_json = Column(JSONB, nullable=True)
    synced_at = Column(DateTime, nullable=True)
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    sample = relationship("Sample", backref="experiments")


class ExperimentSubmission(Base):
    """
    ExperimentSubmission model for storing experiment data staged for submission to ENA.
    
    This model corresponds to the 'experiment_submission' table in the database.
    """
    __tablename__ = "experiment_submission"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiment.id"), nullable=True)
    experiment_accession = Column(Text, nullable=True)
    run_accession = Column(Text, nullable=True)
    sample_id = Column(UUID(as_uuid=True), ForeignKey("sample.id"), nullable=True)
    internal_json = Column(JSONB, nullable=True)
    submission_json = Column(JSONB, nullable=True)
    submission_at = Column(DateTime, nullable=True)
    status = Column(SQLAlchemyEnum("draft", "ready", "submission", "rejected", name="submission_status"), nullable=False, default="draft")
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    experiment = relationship("Experiment", backref="submission_records")
    sample = relationship("Sample")


class ExperimentFetched(Base):
    """
    ExperimentFetched model for storing immutable history of experiment data from ENA.
    
    This model corresponds to the 'experiment_fetched' table in the database.
    """
    __tablename__ = "experiment_fetched"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiment.id"), nullable=True)
    experiment_accession = Column(Text, nullable=False)
    run_accession = Column(Text, nullable=False)
    sample_id = Column(UUID(as_uuid=True), ForeignKey("sample.id"), nullable=True)
    raw_json = Column(JSONB, nullable=True)
    fetched_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    experiment = relationship("Experiment", backref="fetched_records")
    sample = relationship("Sample")
