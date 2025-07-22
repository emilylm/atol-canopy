import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class BPAInitiative(Base):
    """
    BPA Initiative model for storing information about physical sample shipments.
    
    This model corresponds to the 'bpa_initiative' table in the database.
    """
    __tablename__ = "bpa_initiative"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bpa_initiative_id_serial = Column(String, unique=True, nullable=False)
    name_vector = Column(Text, nullable=False)
    shipment_accession = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
