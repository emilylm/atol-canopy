import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Text, BigInteger, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


class Read(Base):
    """
    Read model for storing data about sequencing reads linked to experiments.
    
    This model corresponds to the 'read' table in the database.
    """
    __tablename__ = "read"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiment.id"), nullable=False)
    bpa_dataset_id = Column(Text, nullable=False)
    bpa_resource_id = Column(Text, nullable=False)
    file_name = Column(Text, nullable=True)
    file_format = Column(Text, nullable=True)
    file_size = Column(BigInteger, nullable=True)
    file_submission_date = Column(Text, nullable=True)
    file_checksum = Column(Text, nullable=True)
    read_access_date = Column(Text, nullable=True)
    bioplatforms_url = Column(Text, nullable=True)
    internal_json = Column(JSONB, nullable=True)
    submitted_json = Column(JSONB, nullable=True)
    status = Column(SQLAlchemyEnum("draft", "submitted", "rejected", name="read_submission_status"), nullable=False, default="draft")
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    experiment = relationship("Experiment", backref="reads")
