"""
Applies application-specific tags to database tables in OpenMetadata using its API.
Processes tables in batches, validates table/tag existence, and provides detailed
logging of operations. Includes dry-run capability to preview changes.

"""

import os
import json
import logging
import requests
from typing import List, Dict
import time
from datetime import datetime
from requests.exceptions import RequestException
import sys
import argparse
from pathlib import Path

def find_project_root(start_path: Path) -> Path:
    """
    Find the project root by looking for the config directory
    """
    current = start_path
    while current != current.parent:  # Stop at root directory
        if (current / "config" / "openmetadata_config.json").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Could not find project root containing config/openmetadata_config.json")

# Project structure constants
SCRIPT_LOCATION = Path(__file__).resolve()
PROJECT_ROOT = find_project_root(SCRIPT_LOCATION)
CONFIG_DIR = PROJECT_ROOT / "config"
LOGS_DIR = PROJECT_ROOT / "logs"

# Debug logging for paths
print(f"Script location: {SCRIPT_LOCATION}")
print(f"Project Root: {PROJECT_ROOT}")
print(f"Config Dir: {CONFIG_DIR}")
print(f"Logs Dir: {LOGS_DIR}")

# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)

# Config file path
CONFIG_FILE = CONFIG_DIR / "openmetadata_config.json"

# List of applications and their corresponding schemas (case-insensitive)
APPLICATION_SCHEMA_MAPPING = {
    'CONSEP': ['consep'],  # Simplified to just match schema
    # Add other applications as needed
}

# Mapping between application names and OpenMetadata tag names
APPLICATION_TAG_MAPPING = {
    'CONSEP': 'CNS',
    # Add other mappings as needed
}

BATCH_SIZE = 100
BATCH_DELAY = 2  # seconds

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {CONFIG_FILE}")
        raise
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in configuration file: {CONFIG_FILE}")
        raise
    except Exception as e:
        logging.error(f"Error loading configuration: {str(e)}")
        raise

def get_tables_for_application(base_url: str, headers: Dict, application: str) -> List[tuple]:
    """
    Get all tables associated with an application by directly querying OpenMetadata.
    
    Args:
        base_url: Base URL for OpenMetadata API
        headers: Request headers including authentication
        application: Application name to match
    
    Returns:
        List of tuples containing (table_name, table_info)
    """
    matched_tables = []
    schemas = APPLICATION_SCHEMA_MAPPING.get(application, [application])
    
    for schema in schemas:
        schema_fqn = f"DBQ01.DBQ01.{schema}"
        endpoint = f"{base_url}/v1/tables"
        params = {
            'databaseSchema': schema_fqn,
            'fields': 'tags,name,fullyQualifiedName',
            'limit': 1000
        }
        
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()
            data = response.json().get('data', [])
            
            for table in data:
                table_info = {
                    'name': table.get('name'),
                    'fqn': table.get('fullyQualifiedName'),
                    'tags': table.get('tags', [])
                }
                matched_tables.append((table.get('name'), table_info))
            
            logging.info(f"Found {len(data)} tables in schema {schema_fqn}")
            
        except Exception as e:
            logging.error(f"Error fetching tables for schema {schema_fqn}: {str(e)}")
    
    # Additional logging for verification
    if matched_tables:
        logging.info(f"Total tables matched for {application}: {len(matched_tables)}")
        logging.info("Table types found:")
        prefixes = {
            'Regular Tables': 'CNS_T_',
            'Views': 'V_',
            'Reference Tables': '',
            'Temporary Tables': 'TEMP_'
        }
        for prefix_type, prefix in prefixes.items():
            count = sum(1 for t in matched_tables if t[0].upper().startswith(prefix.upper()))
            logging.info(f"  {prefix_type}: {count}")
    else:
        logging.warning(f"No tables matched for application {application}. Schemas searched: {schemas}")
    
    return matched_tables

def check_table_exists(base_url, headers, table_fqn):
    try:
        encoded_fqn = requests.utils.quote(table_fqn)
        response = requests.get(f"{base_url}/v1/tables/name/{encoded_fqn}", headers=headers)
        return response.status_code == 200
    except Exception as e:
        logging.error(f"Error checking table existence: {str(e)}")
        return False

def check_tag_exists(base_url, headers, tag_fqn):
    try:
        encoded_fqn = requests.utils.quote(tag_fqn)
        response = requests.get(f"{base_url}/v1/tags/name/{encoded_fqn}", headers=headers)
        return response.status_code == 200
    except Exception as e:
        logging.error(f"Error checking tag existence: {str(e)}")
        return False

def apply_tag(base_url, headers, table_fqn, tag_fqn, dry_run=False, max_retries=3, retry_delay=5):
    encoded_fqn = requests.utils.quote(table_fqn)
    url = f"{base_url}/v1/tables/name/{encoded_fqn}"
    
    for attempt in range(max_retries):
        try:
            # First, get the current table metadata
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            table_data = response.json()
            
            # Check if the tag is already applied
            existing_tags = table_data.get('tags', [])
            if any(tag.get('tagFQN') == tag_fqn for tag in existing_tags):
                logging.info(f"Tag '{tag_fqn}' is already applied to table '{table_fqn}'")
                return True

            if dry_run:
                logging.info(f"[DRY RUN] Would apply tag '{tag_fqn}' to table '{table_fqn}'")
                return True

            # Prepare the patch operation
            patch_operation = [
                {
                    "op": "add",
                    "path": "/tags/-",
                    "value": {"tagFQN": tag_fqn}
                }
            ]

            # Set the correct Content-Type for JSON Patch
            patch_headers = headers.copy()
            patch_headers['Content-Type'] = 'application/json-patch+json'

            # Apply the PATCH operation
            patch_response = requests.patch(url, headers=patch_headers, json=patch_operation)
            patch_response.raise_for_status()
            
            logging.info(f"Successfully applied tag '{tag_fqn}' to table '{table_fqn}'")
            return True

        except RequestException as e:
            if attempt < max_retries - 1:
                logging.warning(f"Attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logging.error(f"Failed to apply tag after {max_retries} attempts.")
                return False

def process_table_batch(base_url, headers, tables, tag_fqn, tag_exists, dry_run=False):
    existing_tables = 0
    missing_tables = 0
    tag_applications = 0
    failed_tag_applications = 0
    already_tagged = 0

    for table_name, table_info in tables:
        if check_table_exists(base_url, headers, table_info['fqn']):
            existing_tables += 1
            current_tags = [tag.get('tagFQN') for tag in table_info.get('tags', [])]
            
            if tag_fqn in current_tags:
                already_tagged += 1
                logging.info(f"Table already has tag '{tag_fqn}': {table_info['fqn']}")
            elif tag_exists:
                if apply_tag(base_url, headers, table_info['fqn'], tag_fqn, dry_run):
                    tag_applications += 1
                else:
                    failed_tag_applications += 1
        else:
            logging.warning(f"Table not found in OpenMetadata API: {table_info['fqn']}")
            missing_tables += 1

    # Batch summary
    logging.info(f"""
    Batch Summary:
    - Tables processed: {len(tables)}
    - Existing tables: {existing_tables}
    - Already tagged: {already_tagged}
    - Would tag (dry run)/Tagged: {tag_applications}
    - Failed operations: {failed_tag_applications}
    - Missing tables: {missing_tables}
    """)

    return existing_tables, missing_tables, tag_applications, failed_tag_applications

def setup_logging(dry_run=False):
    """Set up logging configuration with both file and console output"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = LOGS_DIR / f'openmetadata_tagging_consep_schema_{timestamp}.log'
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
    
    # File handler
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    run_type = "[DRY RUN] " if dry_run else ""
    logger.info(f"--- New {run_type}Run Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

def parse_arguments():
    parser = argparse.ArgumentParser(description='OpenMetadata Table Tagging Script')
    parser.add_argument('--dry-run', action='store_true', 
                      help='Perform a dry run without applying any tags')
    return parser.parse_args()

def main():
    args = parse_arguments()
    setup_logging(args.dry_run)

    try:
        config = load_config()
        
        base_url = config['base_url']
        jwt_token = config['jwt_token']
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }

        total_applications_processed = 0
        total_tables = 0
        total_existing_tables = 0
        total_missing_tables = 0
        existing_tags = 0
        missing_tags = 0
        total_tag_applications = 0
        total_failed_tag_applications = 0

        # Process each application
        for application in APPLICATION_SCHEMA_MAPPING.keys():
            openmetadata_tag = APPLICATION_TAG_MAPPING.get(application, application)
            tag_fqn = f"Application System.{openmetadata_tag}"
            
            logging.info(f"Processing application: {application}")
            logging.info(f"Using OpenMetadata tag: {openmetadata_tag}")

            # Get all tables directly from OpenMetadata
            tables = get_tables_for_application(base_url, headers, application)
            logging.info(f"Found {len(tables)} tables with schema matching {application}")

            tag_exists = check_tag_exists(base_url, headers, tag_fqn)
            if tag_exists:
                existing_tags += 1
                logging.info(f"Tag '{tag_fqn}' exists in OpenMetadata.")
            else:
                missing_tags += 1
                logging.warning(f"Tag '{tag_fqn}' does not exist in OpenMetadata.")

            total_tables += len(tables)

            # Process tables in batches
            for i in range(0, len(tables), BATCH_SIZE):
                batch = tables[i:i+BATCH_SIZE]
                existing, missing, applied, failed = process_table_batch(
                    base_url, headers, batch, tag_fqn, tag_exists, args.dry_run
                )
                total_existing_tables += existing
                total_missing_tables += missing
                total_tag_applications += applied
                total_failed_tag_applications += failed

                if i + BATCH_SIZE < len(tables):
                    logging.info(f"Waiting {BATCH_DELAY} seconds before processing next batch...")
                    time.sleep(BATCH_DELAY)

            total_applications_processed += 1

        run_type = "[DRY RUN] " if args.dry_run else ""
        summary = f"""
        {run_type}Run Summary:
        Total applications processed: {total_applications_processed}
        Total tables checked: {total_tables}
        Existing tables in OpenMetadata: {total_existing_tables}
        Missing tables in OpenMetadata: {total_missing_tables}
        Existing tags in OpenMetadata: {existing_tags}
        Missing tags in OpenMetadata: {missing_tags}
        {"Would apply" if args.dry_run else "Applied"} tags successfully: {total_tag_applications}
        Failed tag applications: {total_failed_tag_applications}
        """
        logging.info(summary)

    except Exception as e:
        logging.error(f"An error occurred in the main script: {str(e)}")
        logging.exception("Full traceback:")
        sys.exit(1)

if __name__ == "__main__":
    main()