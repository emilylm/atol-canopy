-- PostgreSQL schema for biological metadata tracking system
-- Based on ER diagram and requirements

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM types
CREATE TYPE submission_status AS ENUM ('draft', 'ready', 'submitted', 'rejected');

-- ==========================================
-- Users and Authentication
-- ==========================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) UNIQUE,
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
    organism_grouping_key TEXT UNIQUE NOT NULL,
    tax_id INTEGER NOT NULL,
    scientific_name TEXT,
    common_name TEXT,
    common_name_source TEXT,
    bpa_json JSONB,
    taxonomy_lineage_json JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
/*
-- BPA organism table
CREATE TABLE organism_bpa (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organism_id UUID REFERENCES organism(id),
    bpa_json JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
*/
-- ==========================================
-- Sample tables
-- ==========================================

-- Main sample table
CREATE TABLE sample (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organism_id UUID REFERENCES organism(id),
    sample_accession TEXT UNIQUE,
    bpa_sample_id TEXT UNIQUE NOT NULL,
    -- Denormalised fields from ENA

    -- BPA fields (bpa_*)
    
    -- Internal AToL fields (internal_* (or atol_*??))

    source_json JSONB,
    synced_at TIMESTAMP,
    last_checked_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Sample submitted table
CREATE TABLE sample_submitted (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sample_id UUID REFERENCES sample(id),
    organism_id UUID REFERENCES organism(id),
    internal_json JSONB,
    submitted_json JSONB,
    submitted_at TIMESTAMP,
    status submission_status NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Sample fetched table
CREATE TABLE sample_fetched (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sample_id UUID REFERENCES sample(id),
    sample_accession TEXT NOT NULL,
    organism_id UUID REFERENCES organism(id),
    raw_json JSONB,
    fetched_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ==========================================
-- Experiment tables
-- ==========================================

-- Main experiment table
CREATE TABLE experiment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sample_id UUID REFERENCES sample(id) NOT NULL,
    experiment_accession TEXT UNIQUE,
    run_accession TEXT UNIQUE,
    source_json JSONB,
    -- Denormalised fields from ENA
    run_read_count TEXT,
    run_base_count TEXT,
    bpa_dataset_id TEXT,
    -- BPA fields (bpa_*)
    bpa_package_id TEXT UNIQUE NOT NULL,
    -- Internal AToL fields (internal_* (or atol_*??))

    synced_at TIMESTAMP,
    last_checked_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Experiment submitted table
CREATE TABLE experiment_submitted (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID REFERENCES experiment(id),
    experiment_accession TEXT,
    run_accession TEXT,
    sample_id UUID REFERENCES sample(id) NOT NULL,
    internal_json JSONB,
    submitted_json JSONB,
    submitted_at TIMESTAMP,
    status submission_status NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Experiment fetched table
CREATE TABLE experiment_fetched (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID REFERENCES experiment(id),
    experiment_accession TEXT NOT NULL,
    run_accession TEXT NOT NULL,
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
    organism_id UUID REFERENCES organism(id) NOT NULL,
    sample_id UUID REFERENCES sample(id) NOT NULL,
    experiment_id UUID REFERENCES experiment(id),
    assembly_accession TEXT UNIQUE,
    -- Denormalised fields from ENA

    -- BPA fields (bpa_*)
    
    -- Internal AToL fields (internal_* (or atol_*??))
    
    source_json JSONB,
    internal_notes TEXT,
    synced_at TIMESTAMP,
    last_checked_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Assembly submitted table
/*
CREATE TABLE assembly_outputs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assembly_id UUID REFERENCES assembly(id),
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
*/

-- Assembly submitted table
CREATE TABLE assembly_submitted (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assembly_id UUID REFERENCES assembly(id),
    organism_id UUID REFERENCES organism(id) NOT NULL,
    sample_id UUID REFERENCES sample(id) NOT NULL,
    experiment_id UUID REFERENCES experiment(id),
    internal_json JSONB,
    submitted_json JSONB,
    submitted_at TIMESTAMP,
    status submission_status NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Assembly fetched table
CREATE TABLE assembly_fetched (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assembly_id UUID REFERENCES assembly(id),
    assembly_accession TEXT NOT NULL,
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
    bioproject_accession TEXT NOT NULL UNIQUE,
    alias TEXT NOT NULL,
    alias_md5 TEXT NOT NULL,
    study_name TEXT NOT NULL,
    new_study_type TEXT,
    study_abstract TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Bioproject experiment table
CREATE TABLE bioproject_experiment (
    bioproject_id UUID REFERENCES bioproject(id) NOT NULL,
    experiment_id UUID REFERENCES experiment(id) NOT NULL,
    PRIMARY KEY (bioproject_id, experiment_id)
);

-- ==========================================
-- Read table (from ER diagram)
-- ==========================================

CREATE TABLE read (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experiment_id UUID REFERENCES experiment(id) NOT NULL,
    internal_json JSONB,
    submitted_json JSONB,
    bpa_dataset_id TEXT,
    bpa_resource_id TEXT,
    file_name TEXT,
    file_format TEXT,
    file_size BIGINT,
    file_submission_date TEXT,
    file_checksum TEXT,
    read_access_date TEXT,
    bioplatforms_url TEXT,
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
    note TEXT,
    other_fields TEXT,
    -- TODO UID or TEXT with semantic versioning?
    version_id UUID,
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Genome note assembly table
CREATE TABLE genome_note_assembly (
    genome_note_id UUID REFERENCES genome_note(id) NOT NULL,
    assembly_id UUID REFERENCES assembly(id) NOT NULL,
    PRIMARY KEY (genome_note_id, assembly_id)
);

-- ==========================================
-- BPA initiative table (from ER diagram)
-- ==========================================

CREATE TABLE bpa_initiative (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    shipment_accession TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for common query patterns
CREATE INDEX idx_organism_id ON organism(id);
CREATE INDEX idx_sample_organism_id ON sample(organism_id);
CREATE INDEX idx_experiment_sample_id ON experiment(sample_id);
CREATE INDEX idx_assembly_sample_id ON assembly(sample_id);
CREATE INDEX idx_assembly_organism_id ON assembly(organism_id);
CREATE INDEX idx_assembly_experiment_id ON assembly(experiment_id);
