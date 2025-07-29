#!/usr/bin/env python3
"""
Standalone script to import BPA data into the database.

This script loads data from JSON files and creates:
1. Organism entities
2. Sample and sample_submitted entities
3. Experiment and experiment_submitted entities

Usage:
    python import_bpa_data_standalone.py
"""

import json
import uuid
import os
from pathlib import Path
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / ".env")

# Get database parameters from environment variables
def get_db_params():
    return {
        "dbname": os.environ.get("ATOL_DB_NAME"),
        "user": os.environ.get("ATOL_DB_USER"),
        "password": os.environ.get("ATOL_DB_PASSWORD"),
        "host": os.environ.get("ATOL_DB_HOST"),
        "port": os.environ.get("ATOL_DB_PORT")
    }

def load_json_file(file_path):
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None


def import_organisms(conn, organisms_data):
    """
    Import organism data into the database.
    
    Args:
        conn: Database connection
        organisms_data: Dictionary of organism data keyed by tax_id
    """
    print(f"Importing {len(organisms_data)} organisms...")
    
    created_count = 0
    skipped_count = 0
    
    cursor = conn.cursor()
    
    for organism_grouping_key, organism_data in organisms_data.items():
        # Extract tax_id from the organism data
        if "taxon_id" in organism_data:
            tax_id = organism_data["taxon_id"]
        else:
            print(f"Warning: Missing taxon_id for {organism_grouping_key}, skipping.")
            skipped_count += 1
            continue
        
        # Check if organism already exists by grouping key
        cursor.execute("SELECT id FROM organism WHERE organism_grouping_key = %s", (organism_grouping_key,))
        existing = cursor.fetchone()
        if existing:
            print(f"Organism with grouping key {organism_grouping_key} already exists, skipping.")
            skipped_count += 1
            continue
        
        # Create new organism
        scientific_name = organism_data.get("scientific_name")
        if not scientific_name:
            print(f"Warning: Missing scientific_name for tax_id {tax_id}, skipping.")
            skipped_count += 1
            continue
        
        try:
            # Generate UUID for organism
            organism_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO organism (id, organism_grouping_key, tax_id, scientific_name, bpa_json)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    organism_id,
                    organism_grouping_key,
                    tax_id,
                    scientific_name,
                    json.dumps(organism_data)
                )
            )
            
            conn.commit()
            created_count += 1
            if created_count % 100 == 0:
                print(f"Created {created_count} organisms...")
        except Exception as e:
            conn.rollback()
            print(f"Error creating organism with tax_id {tax_id}: {e}")
            skipped_count += 1
    
    print(f"Organism import complete. Created: {created_count}, Skipped: {skipped_count}")
    return created_count


def import_samples(conn, samples_data):
    """
    Import sample data into the database.
    
    Args:
        conn: Database connection
        samples_data: Dictionary of sample data keyed by bpa_sample_id
    """
    print(f"Importing {len(samples_data)} samples...")
    
    created_samples_count = 0
    created_submitted_count = 0
    skipped_count = 0
    
    cursor = conn.cursor()
    
    for bpa_sample_id, sample_data in samples_data.items():
        # Check if sample already exists
        cursor.execute("SELECT id FROM sample WHERE bpa_sample_id = %s", (bpa_sample_id,))
        existing = cursor.fetchone()
        if existing:
            print(f"Sample with name {bpa_sample_id} already exists, skipping.")
            skipped_count += 1
            continue
        
        # Get organism reference from sample data
        organism_id = None
        if "organism_grouping_key" in sample_data:
            organism_grouping_key = sample_data["organism_grouping_key"]
            # Look up the organism ID by grouping key
            cursor.execute("SELECT id FROM organism WHERE organism_grouping_key = %s", (organism_grouping_key,))
            organism_result = cursor.fetchone()
            if organism_result:
                organism_id = organism_result[0]
            else:
                print(f"Warning: Organism with grouping key {organism_grouping_key} not found for sample {bpa_sample_id}. Creating sample without organism reference.")
        
        try:
            # Create new sample
            sample_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO sample (id, organism_id, bpa_sample_id, source_json)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (
                    sample_id,
                    organism_id,
                    bpa_sample_id,
                    json.dumps(sample_data)
                )
            )


            # Create sample_submitted record
            cursor.execute(
                """
                INSERT INTO sample_submitted (id, sample_id, organism_id, internal_json)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    str(uuid.uuid4()),
                    sample_id,
                    organism_id,
                    json.dumps(sample_data)
                )
            )
            
            conn.commit()
            created_samples_count += 1
            created_submitted_count += 1
            
            if created_samples_count % 100 == 0:
                print(f"Created {created_samples_count} samples...")
                
        except Exception as e:
            conn.rollback()
            print(f"Error creating sample {bpa_sample_id}: {e}")
            skipped_count += 1
    
    print(f"Sample import complete. Created samples: {created_samples_count}, "
          f"Created submitted records: {created_submitted_count}, Skipped: {skipped_count}")
    return created_samples_count


def import_experiments(conn, experiments_data):
    """
    Import experiment data into the database.
    
    Args:
        conn: Database connection
        experiments_data: Dictionary of experiment data keyed by package_id
    """
    print(f"Importing experiments from {len(experiments_data)} experiment packages...")
    
    created_experiments_count = 0
    created_submitted_count = 0
    skipped_count = 0
    
    cursor = conn.cursor()
    
    for package_id, experiment_data in experiments_data.items():
        # Check if experiment data contains bpa_sample_id
        if 'bpa_sample_id' not in experiment_data:
            print(f"No bpa_sample_id found for experiment package {package_id}, skipping.")
            skipped_count += 1
            continue
                
        bpa_sample_id = experiment_data['bpa_sample_id']

        # Get sample id from sample name
        cursor.execute("SELECT id FROM sample WHERE bpa_sample_id = %s", (bpa_sample_id,))
        sample_id = cursor.fetchone()
        if not sample_id:
            print(f"Sample with name {bpa_sample_id} not found, skipping.")
            skipped_count += 1
            continue

        try:
            # Create new experiment
            experiment_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO experiment (
                    id, sample_id, bpa_package_id
                )
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (
                    experiment_id,
                    sample_id,
                    package_id,
                )
            )
            
            # Create experiment_submitted record
            cursor.execute(
                """
                INSERT INTO experiment_submitted (
                    id, experiment_id, sample_id, internal_json
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    str(uuid.uuid4()),
                    experiment_id,
                    sample_id,
                    json.dumps(experiment_data)
                )
            )
            
            conn.commit()
            created_experiments_count += 1
            created_submitted_count += 1
            
            if created_experiments_count % 100 == 0:
                print(f"Created {created_experiments_count} experiments...")
                
        except Exception as e:
            conn.rollback()
            print(f"Error creating experiment {package_id}: {e}")
            skipped_count += 1
    
    print(f"Experiment import complete. Created experiments: {created_experiments_count}, "
          f"Created submitted records: {created_submitted_count}, Skipped: {skipped_count}")
    
    return created_experiments_count


def main():
    """Main function to import all BPA data."""
    # Get database parameters from environment variables or defaults
    db_params = get_db_params()
    
    # Define file paths
    data_dir = Path(__file__).parent.parent / "data"
    organisms_file = data_dir / "unique_organisms.json"
    samples_file = data_dir / "unique_samples.json"
    experiments_file = data_dir / "experiments.json"
    
    # Check if files exist
    for file_path in [organisms_file, samples_file, experiments_file]:
        if not file_path.exists():
            print(f"Error: {file_path} not found.")
            return
    
    # Load data
    print("Loading data files...")
    organisms_data = load_json_file(organisms_file)
    samples_data = load_json_file(samples_file)
    experiments_data = load_json_file(experiments_file)
    
    if not all([organisms_data, samples_data, experiments_data]):
        print("Error loading data files.")
        return
    
    # Connect to the database
    try:
        print(f"Connecting to database with parameters: {db_params}")
        conn = psycopg2.connect(**db_params)
        psycopg2.extras.register_uuid()
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return
    
    try:
        # Import data
        print("\n=== Starting BPA Data Import ===\n")
        
        # 1. Import organisms
        print("\n--- Importing Organisms ---\n")
        organisms_count = import_organisms(conn, organisms_data)
        
        # 2. Import samples
        print("\n--- Importing Samples ---\n")
        samples_count = import_samples(conn, samples_data)
        
        # 3. Import experiments
        print("\n--- Importing Experiments ---\n")
        experiments_count = import_experiments(conn, experiments_data)
        
        print("\n=== BPA Data Import Complete ===\n")
        print(f"Summary:")
        print(f"- Organisms created: {organisms_count}")
        print(f"- Samples created: {samples_count}")
        print(f"- Experiments created: {experiments_count}")
        
    except Exception as e:
        print(f"Error during import: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
    
# Usage examples:
# python3 import_bpa_data_standalone.py  # Uses default parameters
# 
# Using environment variables:
# ATOL_DB_HOST=localhost ATOL_DB_PORT=5433 ATOL_DB_NAME=atol_db ATOL_DB_USER=postgres ATOL_DB_PASSWORD=postgres python3 import_bpa_data_standalone.py
# 
# You can also set environment variables in your shell before running:
# export ATOL_DB_HOST=localhost
# export ATOL_DB_PORT=5433
# export ATOL_DB_NAME=atol_db
# export ATOL_DB_USER=postgres
# export ATOL_DB_PASSWORD=postgres
# python3 import_bpa_data_standalone.py

# organism: 162
# sample: 1465
# experimemt: 1527
