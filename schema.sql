-- PostgreSQL schema for biological metadata tracking system
-- Based on ER diagram and requirements

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- Users and Authentication
-- ==========================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    roles TEXT[] NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==========================================
-- Organism tables
-- ==========================================

-- Main organism table
CREATE TABLE organism (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organism_id_serial TEXT NOT NULL UNIQUE,
    tax_id INTEGER UNIQUE NOT NULL,
    species_taxid_id INTEGER NOT NULL,
    scientific_name_taxon TEXT NOT NULL,
    common_name_vector TEXT,
    taxonomy_lineage_json JSONB,
    species_organism_json JSONB,
    source_json JSONB,
    internal_notes TEXT,
    synced_at TIMESTAMP,
    last_checked_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Organism submitted table
CREATE TABLE organism_submitted (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organism_id UUID REFERENCES organism(id),
    organism_id_serial TEXT NOT NULL,
    tax_id INTEGER NOT NULL,
    species_taxid_id INTEGER NOT NULL,
    scientific_name_taxon TEXT NOT NULL,
    common_name_vector TEXT,
    taxonomy_lineage_json JSONB,
    species_organism_json JSONB,
    submitted_json JSONB,
    status TEXT NOT NULL CHECK (status IN ('draft', 'submitted', 'rejected')),
    submitted_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Organism fetched table
CREATE TABLE organism_fetched (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organism_id UUID REFERENCES organism(id),
    organism_id_serial TEXT NOT NULL,
    tax_id INTEGER NOT NULL,
    species_taxid_id INTEGER NOT NULL,
    scientific_name_taxon TEXT NOT NULL,
    common_name_vector TEXT,
    taxonomy_lineage_json JSONB,
    species_organism_json JSONB,
    fetched_json JSONB,
    fetched_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==========================================
-- Sample tables
-- ==========================================

-- Main sample table
CREATE TABLE sample (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sample_id_serial TEXT NOT NULL UNIQUE,
    organism_id UUID REFERENCES organism(id),
    sample_accession_vector TEXT UNIQUE,
    source_json JSONB,
    internal_notes TEXT,
    internal_priority_flag TEXT,
    synced_at TIMESTAMP,
    last_checked_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Sample submitted table
CREATE TABLE sample_submitted (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sample_id UUID REFERENCES sample(id),
    sample_id_serial TEXT NOT NULL,
    organism_id UUID REFERENCES organism(id),
    submitted_json JSONB,
    submitted_at TIMESTAMP,
    status TEXT NOT NULL CHECK (status IN ('draft', 'submitted', 'rejected')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Sample fetched table
CREATE TABLE sample_fetched (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sample_id UUID REFERENCES sample(id),
    sample_id_serial TEXT NOT NULL,
    sample_accession_vector TEXT NOT NULL,
    organism_id UUID REFERENCES organism(id),
    raw_json JSONB,
    fetched_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Sample relationships table
CREATE TABLE sample_relationship (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_sample_id UUID REFERENCES sample(id) NOT NULL,
    target_sample_id UUID REFERENCES sample(id) NOT NULL,
    relationship_type TEXT NOT NULL CHECK (relationship_type IN ('derived_from', 'subsample_of', 'parent_of', 'child_of')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_sample_relationship UNIQUE (source_sample_id, target_sample_id, relationship_type)
);

-- ==========================================
-- Experiment tables
-- ==========================================

-- Main experiment table
CREATE TABLE experiment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id_serial TEXT NOT NULL UNIQUE,
    sample_id UUID REFERENCES sample(id) NOT NULL,
    experiment_accession_vector TEXT UNIQUE NOT NULL,
    run_accession_text UUID UNIQUE NOT NULL,
    source_json JSONB,
    internal_notes TEXT,
    internal_priority_flag TEXT,
    synced_at TIMESTAMP,
    last_checked_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Experiment submitted table
CREATE TABLE experiment_submitted (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID REFERENCES experiment(id),
    experiment_id_serial TEXT NOT NULL,
    experiment_accession_vector TEXT,
    run_accession_text UUID,
    sample_id UUID REFERENCES sample(id) NOT NULL,
    submitted_json JSONB,
    submitted_at TIMESTAMP,
    status TEXT NOT NULL CHECK (status IN ('draft', 'submitted', 'rejected')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Experiment fetched table
CREATE TABLE experiment_fetched (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID REFERENCES experiment(id),
    experiment_id_serial TEXT NOT NULL,
    experiment_accession_vector TEXT NOT NULL,
    run_accession_text UUID NOT NULL,
    sample_id UUID REFERENCES sample(id) NOT NULL,
    raw_json JSONB,
    fetched_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==========================================
-- Assembly tables
-- ==========================================

-- Main assembly table
CREATE TABLE assembly (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assembly_id_serial TEXT NOT NULL UNIQUE,
    organism_id UUID REFERENCES organism(id) NOT NULL,
    sample_id UUID REFERENCES sample(id) NOT NULL,
    experiment_id UUID REFERENCES experiment(id),
    assembly_accession_vector TEXT UNIQUE,
    source_json JSONB,
    internal_notes TEXT,
    synced_at TIMESTAMP,
    last_checked_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Assembly submitted table
CREATE TABLE assembly_submitted (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assembly_id UUID REFERENCES assembly(id),
    assembly_id_serial TEXT NOT NULL,
    organism_id UUID REFERENCES organism(id) NOT NULL,
    sample_id UUID REFERENCES sample(id) NOT NULL,
    experiment_id UUID REFERENCES experiment(id),
    submitted_json JSONB,
    submitted_at TIMESTAMP,
    status TEXT NOT NULL CHECK (status IN ('draft', 'submitted', 'rejected')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Assembly fetched table
CREATE TABLE assembly_fetched (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assembly_id UUID REFERENCES assembly(id),
    assembly_id_serial TEXT NOT NULL,
    assembly_accession_vector TEXT NOT NULL,
    organism_id UUID REFERENCES organism(id) NOT NULL,
    sample_id UUID REFERENCES sample(id) NOT NULL,
    experiment_id UUID REFERENCES experiment(id),
    fetched_json JSONB,
    fetched_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==========================================
-- Bioproject tables (from ER diagram)
-- ==========================================

-- Main bioproject table
CREATE TABLE bioproject (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bioproject_accession_vector TEXT NOT NULL UNIQUE,
    alias_vector TEXT NOT NULL,
    alias_vector_md5 TEXT NOT NULL,
    study_name_vector TEXT NOT NULL,
    new_study_type TEXT,
    study_abstract_vector TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Bioproject experiment table
CREATE TABLE bioproject_experiment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bioproject_id UUID REFERENCES bioproject(id) NOT NULL,
    experiment_id UUID REFERENCES experiment(id) NOT NULL,
    bioproject_accession_vector TEXT NOT NULL,
    experiment_id_serial TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_bioproject_experiment UNIQUE (bioproject_id, experiment_id)
);

-- ==========================================
-- Read table (from ER diagram)
-- ==========================================

CREATE TABLE read (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    read_id_serial TEXT NOT NULL UNIQUE,
    experiment_id UUID REFERENCES experiment(id) NOT NULL,
    dataset_name_vector TEXT NOT NULL,
    file_name TEXT,
    file_format TEXT,
    file_size BIGINT,
    file_extension_date TEXT,
    file_md5 TEXT,
    read_access_date TIMESTAMP,
    parameters_url TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==========================================
-- Genome note tables (from ER diagram)
-- ==========================================

-- Main genome_note table
CREATE TABLE genome_note (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    genome_note_id_serial TEXT NOT NULL UNIQUE,
    organism_id UUID REFERENCES organism(id) NOT NULL,
    note_vector TEXT,
    other_fields TEXT,
    version_chain_id UUID,
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Genome note assembly table
CREATE TABLE genome_note_assembly (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    genome_note_id UUID REFERENCES genome_note(id) NOT NULL,
    assembly_id UUID REFERENCES assembly(id) NOT NULL,
    genome_note_id_serial TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_genome_note_assembly UNIQUE (genome_note_id, assembly_id)
);

-- ==========================================
-- BPA initiative table (from ER diagram)
-- ==========================================

CREATE TABLE bpa_initiative (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bpa_initiative_id_serial TEXT NOT NULL UNIQUE,
    name_vector TEXT NOT NULL,
    shipment_accession TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for common query patterns
CREATE INDEX idx_organism_tax_id ON organism(tax_id);
CREATE INDEX idx_sample_organism_id ON sample(organism_id);
CREATE INDEX idx_experiment_sample_id ON experiment(sample_id);
CREATE INDEX idx_assembly_sample_id ON assembly(sample_id);
CREATE INDEX idx_assembly_organism_id ON assembly(organism_id);
CREATE INDEX idx_assembly_experiment_id ON assembly(experiment_id);
