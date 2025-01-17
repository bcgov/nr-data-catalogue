import json
import os
from pathlib import Path
import logging
from datetime import datetime

# Get the absolute path to the script itself
SCRIPT_PATH = os.path.abspath(__file__)
# Get the script's directory (schema_tagging)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
# Get src directory
SRC_DIR = os.path.dirname(SCRIPT_DIR)
# Get the project root (parent of src)
PROJECT_ROOT = os.path.dirname(SRC_DIR)
# Define other directory paths
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')

def setup_logging():
    """Set up basic logging to both file and console"""
    log_file = os.path.join(LOGS_DIR, 'mapping_cleaner.log')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logging.info(f"=== New Mapping Cleaning Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

def should_include_entry(name: str) -> bool:
    """Check if the entry should be included in the cleaned mapping"""
    excluded_prefixes = ['CONSEP', 'THE']
    return not any(name.startswith(prefix) for prefix in excluded_prefixes)

def clean_name(name: str) -> str:
    """
    Clean name in two steps:
    1. First remove dash and everything after it
    2. Then remove _REPLICATION if present
    
    Examples:
    - 'ATS - GEOTST' -> 'ATS'
    - 'ATS_REPLICATION - odsdev' -> 'ATS'
    - 'FTA_REPLICATION - odstst' -> 'FTA'
    """
    # First remove dash and everything after it
    name = name.split(' - ')[0]
    
    # Then remove _REPLICATION if present
    name = name.replace('_REPLICATION', '')
    
    return name.strip()

def clean_service_name(service: str) -> str:
    """Clean service name for use in key generation"""
    service = service.replace(' Test Database', '')
    if 'Operational Data Store' in service:
        if 'DEV' in service:
            return 'ODS_DEV'
        elif 'TEST' in service:
            return 'ODS_TEST'
        return 'ODS'
    return service

def create_unique_key(cleaned_name: str, service: str) -> str:
    """Create a unique key using the cleaned name and service"""
    service_key = clean_service_name(service)
    return f"{cleaned_name}_{service_key}"

def clean_mapping_names(mapping_file: str):
    """Clean application and tag names in the mapping file"""
    # Read the original mapping
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)

    # Create new mapping with cleaned names, excluding specific entries
    cleaned_mapping = {}
    excluded_entries = []
    cleaned_entries = []
    
    for app_name, details in mapping.items():
        if should_include_entry(app_name):
            original_name = app_name
            # Track intermediate state for logging
            after_dash_removal = app_name.split(' - ')[0]
            final_cleaned_name = clean_name(app_name)
            
            service = details['service']
            unique_key = create_unique_key(final_cleaned_name, service)
            
            cleaned_details = details.copy()
            cleaned_details['tag_name'] = clean_name(details['tag_name'])
            
            cleaned_mapping[unique_key] = cleaned_details
            
            # Log the cleaning steps if there were changes
            if original_name != unique_key:
                cleaned_entries.append({
                    'original': original_name,
                    'after_dash_removal': after_dash_removal,
                    'after_replication_removal': final_cleaned_name,
                    'final_key': unique_key
                })
        else:
            excluded_entries.append(app_name)

    # Overwrite the original file with cleaned mapping
    with open(mapping_file, 'w') as f:
        json.dump(cleaned_mapping, f, indent=4)

    logging.info(f"Original mapping file has been cleaned and updated: {mapping_file}")
    
    # Print summary of changes
    logging.info(f"\nTotal entries processed: {len(mapping)}")
    logging.info(f"Entries in cleaned mapping: {len(cleaned_mapping)}")
    logging.info(f"Entries removed: {len(excluded_entries)}")
    
    if excluded_entries:
        logging.info("\nRemoved entries:")
        for entry in excluded_entries:
            logging.info(f"- {entry}")
            
    if cleaned_entries:
        logging.info("\nCleaning steps for modified entries:")
        for entry in cleaned_entries:
            logging.info(f"\nOriginal: {entry['original']}")
            logging.info(f"After dash removal: {entry['after_dash_removal']}")
            logging.info(f"After _REPLICATION removal: {entry['after_replication_removal']}")
            logging.info(f"Final key: {entry['final_key']}")

def main():
    try:
        # Set up logging
        setup_logging()
        
        # Debug path information
        logging.info(f"Project Root: {PROJECT_ROOT}")
        logging.info(f"Data Directory: {DATA_DIR}")
        
        # Input file path (will be overwritten)
        mapping_file = os.path.join(DATA_DIR, 'application_mapping.json')
        logging.info(f"Processing mapping file: {mapping_file}")
        
        # Clean the mapping
        clean_mapping_names(mapping_file)
        
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()