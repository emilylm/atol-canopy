import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Bioproject(Base):
    """
    Bioproject model for storing project information linked to experiments.
    
    This model corresponds to the 'bioproject' table in the database.
    """
    __tablename__ = "bioproject"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bioproject_accession = Column(Text, unique=True, nullable=False)
    alias = Column(Text, nullable=False)
    alias_md5 = Column(Text, nullable=False)
    study_name = Column(Text, nullable=False)
    new_study_type = Column(Text, nullable=True)
    study_abstract = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


class BioprojectExperiment(Base):
    """
    BioprojectExperiment model for linking bioprojects to experiments.
    
    This model corresponds to the 'bioproject_experiment' table in the database.
    """
    __tablename__ = "bioproject_experiment"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bioproject_id = Column(UUID(as_uuid=True), ForeignKey("bioproject.id"), nullable=False)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiment.id"), nullable=False)
    bioproject_accession = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    bioproject = relationship("Bioproject", backref="bioproject_experiments")
    experiment = relationship("Experiment", backref="bioproject_experiments")
