import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.session import Base


class Organism(Base):
    """
    Organism model for storing taxonomic information.
    
    This model corresponds to the 'organism' table in the database.
    """
    __tablename__ = "organism"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organism_id_serial = Column(String, unique=True, nullable=False)
    tax_id = Column(Integer, unique=True, nullable=False)
    species_taxid_id = Column(Integer, nullable=False)
    scientific_name_taxon = Column(Text, nullable=False)
    common_name_vector = Column(Text, nullable=True)
    taxonomy_lineage_json = Column(JSONB, nullable=True)
    species_organism_json = Column(JSONB, nullable=True)
    source_json = Column(JSONB, nullable=True)
    internal_notes = Column(Text, nullable=True)
    synced_at = Column(DateTime, nullable=True)
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class OrganismSubmitted(Base):
    """
    OrganismSubmitted model for storing organism data staged for submission to ENA.
    
    This model corresponds to the 'organism_submitted' table in the database.
    """
    __tablename__ = "organism_submitted"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organism_id = Column(UUID(as_uuid=True), nullable=True)
    organism_id_serial = Column(String, nullable=False)
    tax_id = Column(Integer, nullable=False)
    species_taxid_id = Column(Integer, nullable=False)
    scientific_name_taxon = Column(Text, nullable=False)
    common_name_vector = Column(Text, nullable=True)
    taxonomy_lineage_json = Column(JSONB, nullable=True)
    species_organism_json = Column(JSONB, nullable=True)
    submitted_json = Column(JSONB, nullable=True)
    status = Column(String, nullable=False)
    submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class OrganismFetched(Base):
    """
    OrganismFetched model for storing immutable history of organism data from ENA.
    
    This model corresponds to the 'organism_fetched' table in the database.
    """
    __tablename__ = "organism_fetched"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organism_id = Column(UUID(as_uuid=True), nullable=True)
    organism_id_serial = Column(String, nullable=False)
    tax_id = Column(Integer, nullable=False)
    species_taxid_id = Column(Integer, nullable=False)
    scientific_name_taxon = Column(Text, nullable=False)
    common_name_vector = Column(Text, nullable=True)
    taxonomy_lineage_json = Column(JSONB, nullable=True)
    species_organism_json = Column(JSONB, nullable=True)
    fetched_json = Column(JSONB, nullable=True)
    fetched_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
