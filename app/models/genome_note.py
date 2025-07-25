import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class GenomeNote(Base):
    """
    GenomeNote model for storing notes and metadata about genomes.
    
    This model corresponds to the 'genome_note' table in the database.
    """
    __tablename__ = "genome_note"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organism_id = Column(UUID(as_uuid=True), ForeignKey("organism.id"), nullable=False)
    note = Column(Text, nullable=True)
    other_fields = Column(Text, nullable=True)
    version_chain_id = Column(UUID(as_uuid=True), nullable=True)
    is_published = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    organism = relationship("Organism", backref="genome_notes")


class GenomeNoteAssembly(Base):
    """
    GenomeNoteAssembly model for linking genome notes to assemblies.
    
    This model corresponds to the 'genome_note_assembly' table in the database.
    """
    __tablename__ = "genome_note_assembly"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    genome_note_id = Column(UUID(as_uuid=True), ForeignKey("genome_note.id"), nullable=False)
    assembly_id = Column(UUID(as_uuid=True), ForeignKey("assembly.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Relationships
    genome_note = relationship("GenomeNote", backref="genome_note_assemblies")
    assembly = relationship("Assembly", backref="genome_note_assemblies")
