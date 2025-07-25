import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.session import Base


class Organism(Base):
    """
    Organism model for storing taxonomic information.
    
    This model corresponds to the 'organism' table in the database.
    """
    __tablename__ = "organism"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organism_grouping_key = Column(Text, unique=True, nullable=False)
    tax_id = Column(Integer, nullable=False)
    scientific_name = Column(Text, nullable=True)
    common_name = Column(Text, nullable=True)
    common_name_source = Column(Text, nullable=True)
    bpa_json = Column(JSONB, nullable=True)
    taxonomy_lineage_json = Column(JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
