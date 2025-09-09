"""
XML generation utilities for ENA submissions.

This module provides functions to generate XML files for various ENA submission types
(samples, experiments, runs, etc.) from the internal JSON representation.
"""
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from typing import Dict, Any, List, Optional
from app.models.organism import Organism
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from app.core.dependencies import get_db


def generate_sample_xml(organism: Organism, submission_json: Dict[str, Any], alias: str, center_name: str = "AToL", 
                       broker_name: str = "AToL", accession: Optional[str] = None) -> str:
    """
    Generate ENA sample XML from submission JSON data.
    
    Args:
        submission_json: Dictionary containing the sample data in the internal format
        alias: Sample alias (typically the sample ID)
        center_name: Center name for the submission
        broker_name: Broker name for the submission
        accession: Optional accession number if the sample is already registered
        
    Returns:
        String containing the XML representation of the sample
    """
    # Create root element
    sample_set = ET.Element("SAMPLE_SET")
    
    # Create sample element with core attributes
    sample = ET.SubElement(sample_set, "SAMPLE")
    sample.set("alias", alias)
    sample.set("center_name", center_name)
    sample.set("broker_name", broker_name)
    if accession:
        sample.set("accession", accession)
    
    identifiers = ET.SubElement(sample, "IDENTIFIERS")
    if accession:
        primary_id = ET.SubElement(identifiers, "PRIMARY_ID")
        primary_id.text = accession
    
    submitter_id = ET.SubElement(identifiers, "SUBMITTER_ID")
    submitter_id.set("namespace", center_name)
    submitter_id.text = alias
    
    title = ET.SubElement(sample, "TITLE")
    title.text = submission_json.get("title", f"{alias}")
    
    sample_name = ET.SubElement(sample, "SAMPLE_NAME")
    
    taxon_id = ET.SubElement(sample_name, "TAXON_ID")
    taxon_id.text = str(organism.tax_id)
    
    scientific_name = ET.SubElement(sample_name, "SCIENTIFIC_NAME")
    scientific_name.text = organism.scientific_name
    
    common_name = ET.SubElement(sample_name, "COMMON_NAME")
    common_name.text = organism.common_name
    
    if "description" in submission_json:
        description = ET.SubElement(sample, "DESCRIPTION")
        description.text = submission_json["description"]
    
    # Add sample attributes
    sample_attributes = ET.SubElement(sample, "SAMPLE_ATTRIBUTES")
    
    # Skip these keys as they are handled separately
    skip_keys = ["title", "taxon_id", "scientific_name", "common_name", "description", "alias"]
    
    # Process all other keys as sample attributes
    for key, value in submission_json.items():
        if key in skip_keys:
            continue

        if value is None:
            continue
            
        attribute = ET.SubElement(sample_attributes, "SAMPLE_ATTRIBUTE")
        
        tag = ET.SubElement(attribute, "TAG")
        tag.text = key
        
        val = ET.SubElement(attribute, "VALUE")
        val.text = str(value)
        
        if key == "geographic location (latitude)" or key == "geographic location (longitude)":
            units = ET.SubElement(attribute, "UNITS")
            units.text = "DD"

    # Check if ENA-CHECKLIST exists before adding it in
    checklist_found = any(attr.find("TAG").text == "ENA-CHECKLIST" 
                         for attr in sample_attributes.findall("SAMPLE_ATTRIBUTE"))
    
    if not checklist_found:
        checklist_attr = ET.SubElement(sample_attributes, "SAMPLE_ATTRIBUTE")
        tag = ET.SubElement(checklist_attr, "TAG")
        tag.text = "ENA-CHECKLIST"
        val = ET.SubElement(checklist_attr, "VALUE")
        val.text = "ERC000053"
    
    # Check project name does not exist before adding it in
    project_name_found = any(attr.find("TAG").text == "project name" 
                         for attr in sample_attributes.findall("SAMPLE_ATTRIBUTE"))
    
    if not project_name_found:
        project_name_attr = ET.SubElement(sample_attributes, "SAMPLE_ATTRIBUTE")
        tag = ET.SubElement(project_name_attr, "TAG")
        tag.text = "project name"
        val = ET.SubElement(project_name_attr, "VALUE")
        val.text = "atol-genome-engine"

    # TO-DO map over mandatory ToL checklist fields and set to "not provided" if they don't yet exist
    # For now, I'm manually adding in a field which doesn't appear in the BPA data:

    # 1. Add collecting institution attribute if not already present
    collecting_institution_found = any(attr.find("TAG").text == "collecting institution" 
                         for attr in sample_attributes.findall("SAMPLE_ATTRIBUTE"))
    
    if not collecting_institution_found:
        collecting_institution_attr = ET.SubElement(sample_attributes, "SAMPLE_ATTRIBUTE")
        tag = ET.SubElement(collecting_institution_attr, "TAG")
        tag.text = "collecting institution"
        val = ET.SubElement(collecting_institution_attr, "VALUE")
        val.text = "not provided"
    
    # Convert to string with proper formatting
    rough_string = ET.tostring(sample_set, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding="UTF-8").decode('UTF-8')

def generate_experiment_xml(submission_json: Dict[str, Any], alias: str, study_accession: Optional[str] = None,
                          study_alias: Optional[str] = None, sample_accession: Optional[str] = None, sample_alias: Optional[str] = None,
                          center_name: str = "AToL", broker_name: str = "AToL", accession: Optional[str] = None) -> str:
    """
    Generate ENA experiment XML from submission JSON data.
    
    Args:
        submission_json: Dictionary containing the experiment data in the internal format
        alias: Experiment alias (typically the experiment ID or BPA package ID)
        center_name: Center name for the submission
        broker_name: Broker name for the submission
        accession: Optional accession number if the experiment is already registered
        
    Returns:
        String containing the XML representation of the experiment
    """
    # Create root element
    experiment_set = ET.Element("EXPERIMENT_SET")
    
    # Create experiment element with attributes
    experiment = ET.SubElement(experiment_set, "EXPERIMENT")
    experiment.set("alias", alias)
    experiment.set("center_name", center_name)
    experiment.set("broker_name", broker_name)
    if accession:
        experiment.set("accession", accession)
    
    # Create identifiers section
    identifiers = ET.SubElement(experiment, "IDENTIFIERS")
    if accession:
        primary_id = ET.SubElement(identifiers, "PRIMARY_ID")
        primary_id.text = accession
    
    submitter_id = ET.SubElement(identifiers, "SUBMITTER_ID")
    submitter_id.set("namespace", center_name)
    submitter_id.text = alias
    
    # Add title
    title = ET.SubElement(experiment, "TITLE")
    title.text = submission_json.get("title", alias)
    
    # TODO study reference
    study_ref = ET.SubElement(experiment, "STUDY_REF")
    if study_accession:
        study_ref.set("accession", study_accession)
    elif study_alias:
        study_ref.set("refname", study_alias)
    else:
        raise HTTPException(status_code=400, detail="Study accession or refname must be provided")
    
    # Add design section
    design = ET.SubElement(experiment, "DESIGN")
    
    # Add design description
    design_description = ET.SubElement(design, "DESIGN_DESCRIPTION")
    design_description.text = submission_json.get("design_description", "")
    
    # Add sample descriptor
    sample_descriptor = ET.SubElement(design, "SAMPLE_DESCRIPTOR")
    if sample_accession:
        sample_descriptor.set("accession", sample_accession)
    elif sample_alias:
        sample_descriptor.set("refname", sample_alias)
    else:
        raise HTTPException(status_code=400, detail="Sample accession or refname must be provided")
    
    # Add library descriptor
    library_descriptor = ET.SubElement(design, "LIBRARY_DESCRIPTOR")
    
    # Add library name
    library_name = ET.SubElement(library_descriptor, "LIBRARY_NAME")
    library_name.text = submission_json.get("library_name", None)
    
    # Add library strategy
    library_strategy = ET.SubElement(library_descriptor, "LIBRARY_STRATEGY")
    library_strategy.text = submission_json.get("library_strategy", None)
    
    # Add library source
    library_source = ET.SubElement(library_descriptor, "LIBRARY_SOURCE")
    library_source.text = submission_json.get("library_source", None)
    
    # Add library selection
    library_selection = ET.SubElement(library_descriptor, "LIBRARY_SELECTION")
    library_selection.text = submission_json.get("library_selection", None)
    
    # Add library construction protocol
    library_construction_protocol = ET.SubElement(library_descriptor, "LIBRARY_CONSTRUCTION_PROTOCOL")
    library_construction_protocol.text = submission_json.get("library_construction_protocol", "unspecified")

    # Add insert size
    insert_size = ET.SubElement(library_descriptor, "INSERT_SIZE")
    insert_size.text = submission_json.get("insert_size", None)

    # Add library layout
    library_layout = ET.SubElement(library_descriptor, "LIBRARY_LAYOUT")
    layout_type = submission_json.get("library_layout", "SINGLE")
    if layout_type == "PAIRED":
        ET.SubElement(library_layout, "PAIRED")
        if "nominal_length" in submission_json:
            paired = library_layout.find("PAIRED")
            paired.set("NOMINAL_LENGTH", str(submission_json["nominal_length"]))
    else:
        ET.SubElement(library_layout, "SINGLE") #TODO check if this is correct
    
    # Add platform section
    platform = ET.SubElement(experiment, "PLATFORM")
    platform_type = submission_json.get("platform", None)
    platform_element = ET.SubElement(platform, platform_type)
    
    # Add instrument model
    instrument_model = ET.SubElement(platform_element, "INSTRUMENT_MODEL")
    instrument_model.text = submission_json.get("instrument_model", None)
    
    # Add experiment attributes if present
    if "attributes" in submission_json and submission_json["attributes"]:
        experiment_attributes = ET.SubElement(experiment, "EXPERIMENT_ATTRIBUTES")
        for key, value in submission_json["attributes"].items():
            if value is None:
                continue
                
            attribute = ET.SubElement(experiment_attributes, "EXPERIMENT_ATTRIBUTE")
            
            tag = ET.SubElement(attribute, "TAG")
            tag.text = key
            
            val = ET.SubElement(attribute, "VALUE")
            val.text = str(value)
    
    # Convert to string with proper formatting
    rough_string = ET.tostring(experiment_set, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding="UTF-8").decode('UTF-8')

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
    return reparsed.toprettyxml(indent="  ", encoding="UTF-8").decode('UTF-8')


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
        
        # Add FILE element
        # First check if files are in a nested 'files' array
        file_element = ET.SubElement(files, "FILE")
        
        # Add file attributes from top-level submission_json
        if "file_checksum" in submission_json:
            file_element.set("checksum", submission_json["file_checksum"])
            file_element.set("checksum_method", "MD5")
        
        if "file_name" in submission_json:
            file_element.set("filename", submission_json["file_name"])
            
        if "file_format" in submission_json:
            file_element.set("filetype", submission_json["file_format"])
    
    # Pretty-print the XML
    rough_string = ET.tostring(run_set, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
