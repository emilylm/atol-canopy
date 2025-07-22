import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Read(Base):
    """
    Read model for storing data about sequencing reads linked to experiments.
    
    This model corresponds to the 'read' table in the database.
    """
    __tablename__ = "read"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    read_id_serial = Column(String, unique=True, nullable=False)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiment.id"), nullable=False)
    dataset_name_vector = Column(Text, nullable=False)
    file_name = Column(Text, nullable=True)
    file_format = Column(Text, nullable=True)
    file_size = Column(BigInteger, nullable=True)
    file_extension_date = Column(Text, nullable=True)
    file_md5 = Column(Text, nullable=True)
    read_access_date = Column(DateTime, nullable=True)
    parameters_url = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    experiment = relationship("Experiment", backref="reads")
