def generate_experiment_xml(submitted_json: Dict[str, Any], alias: str, center_name: str = "AToL",
                          broker_name: str = "AToL", accession: Optional[str] = None) -> str:
    """
    Generate ENA experiment XML from submitted JSON data.
    
    Args:
        submitted_json: Dictionary containing the experiment data in the internal format
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
    title.text = submitted_json.get("title", f"{alias} experiment")
    
    # Add study reference
    study_ref = ET.SubElement(experiment, "STUDY_REF")
    if "study_accession" in submitted_json:
        study_ref.set("accession", submitted_json["study_accession"])
    else:
        study_ref.set("refname", submitted_json.get("study_refname", "AToL_study"))
    
    # Add design section
    design = ET.SubElement(experiment, "DESIGN")
    
    # Add design description
    design_description = ET.SubElement(design, "DESIGN_DESCRIPTION")
    design_description.text = submitted_json.get("design_description", "")
    
    # Add sample descriptor
    sample_descriptor = ET.SubElement(design, "SAMPLE_DESCRIPTOR")
    if "sample_accession" in submitted_json:
        sample_descriptor.set("accession", submitted_json["sample_accession"])
    elif "sample_refname" in submitted_json:
        sample_descriptor.set("refname", submitted_json["sample_refname"])
    
    # Add library descriptor
    library_descriptor = ET.SubElement(design, "LIBRARY_DESCRIPTOR")
    
    # Add library name
    library_name = ET.SubElement(library_descriptor, "LIBRARY_NAME")
    library_name.text = submitted_json.get("library_name", "")
    
    # Add library strategy
    library_strategy = ET.SubElement(library_descriptor, "LIBRARY_STRATEGY")
    library_strategy.text = submitted_json.get("library_strategy", "OTHER")
    
    # Add library source
    library_source = ET.SubElement(library_descriptor, "LIBRARY_SOURCE")
    library_source.text = submitted_json.get("library_source", "GENOMIC")
    
    # Add library selection
    library_selection = ET.SubElement(library_descriptor, "LIBRARY_SELECTION")
    library_selection.text = submitted_json.get("library_selection", "unspecified")
    
    # Add library layout
    library_layout = ET.SubElement(library_descriptor, "LIBRARY_LAYOUT")
    layout_type = submitted_json.get("library_layout", "SINGLE")
    if layout_type == "PAIRED":
        ET.SubElement(library_layout, "PAIRED")
        if "nominal_length" in submitted_json:
            paired = library_layout.find("PAIRED")
            paired.set("NOMINAL_LENGTH", str(submitted_json["nominal_length"]))
    else:
        ET.SubElement(library_layout, "SINGLE")
    
    # Add platform section
    platform = ET.SubElement(experiment, "PLATFORM")
    platform_type = submitted_json.get("platform", "ILLUMINA")
    platform_element = ET.SubElement(platform, platform_type)
    
    # Add instrument model
    instrument_model = ET.SubElement(platform_element, "INSTRUMENT_MODEL")
    instrument_model.text = submitted_json.get("instrument_model", "unspecified")
    
    # Add experiment attributes if present
    if "attributes" in submitted_json and submitted_json["attributes"]:
        experiment_attributes = ET.SubElement(experiment, "EXPERIMENT_ATTRIBUTES")
        for key, value in submitted_json["attributes"].items():
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
    return reparsed.toprettyxml(indent="  ")


def generate_experiments_xml(experiments_data: List[Dict[str, Any]]) -> str:
    """
    Generate ENA experiment XML for multiple experiments.
    
    Args:
        experiments_data: List of dictionaries, each containing:
            - submitted_json: Dictionary with experiment data
            - alias: Experiment alias
            - center_name: (Optional) Center name
            - broker_name: (Optional) Broker name
            - accession: (Optional) Accession number
            
    Returns:
        String containing the XML representation of all experiments
    """
    # Create root element
    experiment_set = ET.Element("EXPERIMENT_SET")
    
    # Add each experiment to the set
    for experiment_data in experiments_data:
        submitted_json = experiment_data["submitted_json"]
        alias = experiment_data["alias"]
        center_name = experiment_data.get("center_name", "AToL")
        broker_name = experiment_data.get("broker_name", "AToL")
        accession = experiment_data.get("accession")
        
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
        title.text = submitted_json.get("title", f"{alias} experiment")
        
        # Add study reference
        study_ref = ET.SubElement(experiment, "STUDY_REF")
        if "study_accession" in submitted_json:
            study_ref.set("accession", submitted_json["study_accession"])
        else:
            study_ref.set("refname", submitted_json.get("study_refname", "AToL_study"))
        
        # Add design section
        design = ET.SubElement(experiment, "DESIGN")
        
        # Add design description
        design_description = ET.SubElement(design, "DESIGN_DESCRIPTION")
        design_description.text = submitted_json.get("design_description", "")
        
        # Add sample descriptor
        sample_descriptor = ET.SubElement(design, "SAMPLE_DESCRIPTOR")
        if "sample_accession" in submitted_json:
            sample_descriptor.set("accession", submitted_json["sample_accession"])
        elif "sample_refname" in submitted_json:
            sample_descriptor.set("refname", submitted_json["sample_refname"])
        
        # Add library descriptor
        library_descriptor = ET.SubElement(design, "LIBRARY_DESCRIPTOR")
        
        # Add library name
        library_name = ET.SubElement(library_descriptor, "LIBRARY_NAME")
        library_name.text = submitted_json.get("library_name", "")
        
        # Add library strategy
        library_strategy = ET.SubElement(library_descriptor, "LIBRARY_STRATEGY")
        library_strategy.text = submitted_json.get("library_strategy", "OTHER")
        
        # Add library source
        library_source = ET.SubElement(library_descriptor, "LIBRARY_SOURCE")
        library_source.text = submitted_json.get("library_source", "GENOMIC")
        
        # Add library selection
        library_selection = ET.SubElement(library_descriptor, "LIBRARY_SELECTION")
        library_selection.text = submitted_json.get("library_selection", "unspecified")
        
        # Add library layout
        library_layout = ET.SubElement(library_descriptor, "LIBRARY_LAYOUT")
        layout_type = submitted_json.get("library_layout", "SINGLE")
        if layout_type == "PAIRED":
            ET.SubElement(library_layout, "PAIRED")
            if "nominal_length" in submitted_json:
                paired = library_layout.find("PAIRED")
                paired.set("NOMINAL_LENGTH", str(submitted_json["nominal_length"]))
        else:
            ET.SubElement(library_layout, "SINGLE")
        
        # Add platform section
        platform = ET.SubElement(experiment, "PLATFORM")
        platform_type = submitted_json.get("platform", "ILLUMINA")
        platform_element = ET.SubElement(platform, platform_type)
        
        # Add instrument model
        instrument_model = ET.SubElement(platform_element, "INSTRUMENT_MODEL")
        instrument_model.text = submitted_json.get("instrument_model", "unspecified")
        
        # Add experiment attributes if present
        if "attributes" in submitted_json and submitted_json["attributes"]:
            experiment_attributes = ET.SubElement(experiment, "EXPERIMENT_ATTRIBUTES")
            for key, value in submitted_json["attributes"].items():
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
    return reparsed.toprettyxml(indent="  ")
