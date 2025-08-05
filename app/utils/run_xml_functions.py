"""
XML generation functions for ENA run submissions.

This module provides utility functions to generate ENA-compliant XML for run submissions.
"""
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom


def generate_run_xml(submission_json: Dict[str, Any], alias: str, center_name: str = "AToL",
                    broker_name: str = "AToL", accession: Optional[str] = None) -> str:
    """
    Generate ENA run XML from submission JSON data.
    
    Args:
        submission_json: Dictionary containing the run data in the internal format
        alias: Run alias (typically the run ID or BPA dataset ID)
        center_name: Center name for the submission
        broker_name: Broker name for the submission
        accession: Optional accession number if the run is already registered
        
    Returns:
        Pretty-printed XML string in ENA run format
    """
    # Create the root element
    run_set = ET.Element("RUN_SET")
    
    # Create the RUN element
    run = ET.SubElement(run_set, "RUN")
    run.set("alias", alias)
    run.set("center_name", center_name)
    run.set("broker_name", broker_name)
    
    # Add accession if provided
    if accession:
        run.set("accession", accession)
    
    # Add IDENTIFIERS section
    identifiers = ET.SubElement(run, "IDENTIFIERS")
    
    # Add PRIMARY_ID if accession is provided
    if accession:
        primary_id = ET.SubElement(identifiers, "PRIMARY_ID")
        primary_id.text = accession
    
    # Add SUBMITTER_ID
    submitter_id = ET.SubElement(identifiers, "SUBMITTER_ID")
    submitter_id.text = alias
    submitter_id.set("namespace", center_name)
    
    # Add EXPERIMENT_REF section
    experiment_ref = ET.SubElement(run, "EXPERIMENT_REF")
    experiment_accession = submission_json.get("experiment_accession")
    
    if experiment_accession:
        experiment_ref.set("accession", experiment_accession)
        
        # Add IDENTIFIERS for experiment reference
        exp_identifiers = ET.SubElement(experiment_ref, "IDENTIFIERS")
        exp_primary_id = ET.SubElement(exp_identifiers, "PRIMARY_ID")
        exp_primary_id.text = experiment_accession
    
    # Add PLATFORM section
    platform = ET.SubElement(run, "PLATFORM")
    platform_type = submission_json.get("platform")
    
    if platform_type:
        platform_element = ET.SubElement(platform, platform_type)
        
        # Add INSTRUMENT_MODEL
        instrument_model = ET.SubElement(platform_element, "INSTRUMENT_MODEL")
        instrument_model.text = submission_json.get("instrument_model")
    
    # Add DATA_BLOCK section
    data_block = ET.SubElement(run, "DATA_BLOCK")
    
    # Add FILES section
    files = ET.SubElement(data_block, "FILES")
    
    # Add FILE element(s)
    if "files" in submission_json and submission_json["files"]:
        for file_data in submission_json["files"]:
            file_element = ET.SubElement(files, "FILE")
            
            # Add file attributes
            if "checksum" in file_data:
                file_element.set("checksum", file_data["checksum"])
                file_element.set("checksum_method", file_data.get("checksum_method", "MD5"))
            
            if "filename" in file_data:
                file_element.set("filename", file_data["filename"])
            
            if "filetype" in file_data:
                file_element.set("filetype", file_data["filetype"])
            
            if "quality_scoring_system" in file_data:
                file_element.set("quality_scoring_system", file_data["quality_scoring_system"])
    
    # Pretty-print the XML
    rough_string = ET.tostring(run_set, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def generate_runs_xml(runs_data: List[Dict[str, Any]]) -> str:
    """
    Generate ENA run XML for multiple runs.
    
    Args:
        runs_data: List of dictionaries, each containing:
            - submission_json: Dictionary with the run data
            - alias: Run alias
            - accession: Optional accession number
            
    Returns:
        Pretty-printed XML string in ENA run format
    """
    # Create the root element
    run_set = ET.Element("RUN_SET")
    
    # Process each run
    for run_data in runs_data:
        submission_json = run_data["submission_json"]
        alias = run_data["alias"]
        accession = run_data.get("accession")
        center_name = run_data.get("center_name", "AToL")
        broker_name = run_data.get("broker_name", "AToL")
        
        # Create the RUN element
        run = ET.SubElement(run_set, "RUN")
        run.set("alias", alias)
        run.set("center_name", center_name)
        run.set("broker_name", broker_name)
        
        # Add accession if provided
        if accession:
            run.set("accession", accession)
        
        # Add IDENTIFIERS section
        identifiers = ET.SubElement(run, "IDENTIFIERS")
        
        # Add PRIMARY_ID if accession is provided
        if accession:
            primary_id = ET.SubElement(identifiers, "PRIMARY_ID")
            primary_id.text = accession
        
        # Add SUBMITTER_ID
        submitter_id = ET.SubElement(identifiers, "SUBMITTER_ID")
        submitter_id.text = alias
        submitter_id.set("namespace", center_name)
        
        # Add EXPERIMENT_REF section
        experiment_ref = ET.SubElement(run, "EXPERIMENT_REF")
        experiment_accession = submission_json.get("experiment_accession")
        
        if experiment_accession:
            experiment_ref.set("accession", experiment_accession)
            
            # Add IDENTIFIERS for experiment reference
            exp_identifiers = ET.SubElement(experiment_ref, "IDENTIFIERS")
            exp_primary_id = ET.SubElement(exp_identifiers, "PRIMARY_ID")
            exp_primary_id.text = experiment_accession
        
        # Add PLATFORM section
        platform = ET.SubElement(run, "PLATFORM")
        platform_type = submission_json.get("platform")
        
        if platform_type:
            platform_element = ET.SubElement(platform, platform_type)
            
            # Add INSTRUMENT_MODEL
            instrument_model = ET.SubElement(platform_element, "INSTRUMENT_MODEL")
            instrument_model.text = submission_json.get("instrument_model")
        
        # Add DATA_BLOCK section
        data_block = ET.SubElement(run, "DATA_BLOCK")
        
        # Add FILES section
        files = ET.SubElement(data_block, "FILES")
        
        # Add FILE element(s)
        if "files" in submission_json and submission_json["files"]:
            for file_data in submission_json["files"]:
                file_element = ET.SubElement(files, "FILE")
                
                # Add file attributes
                if "checksum" in file_data:
                    file_element.set("checksum", file_data["checksum"])
                    file_element.set("checksum_method", file_data.get("checksum_method", "MD5"))
                
                if "filename" in file_data:
                    file_element.set("filename", file_data["filename"])
                
                if "filetype" in file_data:
                    file_element.set("filetype", file_data["filetype"])
                
                if "quality_scoring_system" in file_data:
                    file_element.set("quality_scoring_system", file_data["quality_scoring_system"])
    
    # Pretty-print the XML
    rough_string = ET.tostring(run_set, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
