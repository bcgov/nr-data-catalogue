import os
import json
import logging
import requests
from datetime import datetime
import sys
import argparse
from typing import List, Dict
from requests.exceptions import RequestException

# Get the absolute path to the script itself
SCRIPT_PATH = os.path.abspath(__file__)
# Get the script's directory
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
# Get the project root (3 levels up from schema_tagging directory)
PROJECT_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR))), 'openmetadata-tagging-project')
# Get the config and data directories
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

# Debug logging to verify paths
print(f"Script Path: {SCRIPT_PATH}")
print(f"Script Directory: {SCRIPT_DIR}")
print(f"Project Root: {PROJECT_ROOT}")
print(f"Config Directory: {CONFIG_DIR}")
print(f"Data Directory: {DATA_DIR}")

"""
Initialize logging configuration for both file and console output.
Creates a log file in the script directory and sets up formatters
for consistent logging across the application.
"""
def setup_logging():
    log_file = os.path.join(PROJECT_ROOT, 'logs', 'openmetadata_schema_tagging.log')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logging.info(f"=== New Table Check and Tagging Run Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

"""
Load the application mapping from a JSON configuration file.
This mapping defines the relationships between applications and their
corresponding service, database, schema, and tag names.
Returns a dictionary containing the application mappings.
"""
def load_application_mapping(mapping_file='application_mapping.json'):
    mapping_path = os.path.join(DATA_DIR, mapping_file)
    try:
        with open(mapping_path, 'r') as f:
            mapping = json.load(f)
            logging.info(f"Successfully loaded application mapping from {mapping_path}")
            return mapping
    except Exception as e:
        logging.error(f"Error loading application mapping file: {str(e)}")
        raise

"""
Initialize the application configuration by loading the mapping file
and creating a list of available applications. Used at startup to
determine which applications can be processed.
Returns a tuple of (mapping_dict, applications_list).
"""
def initialize_applications():
    try:
        mapping = load_application_mapping()
        return mapping, list(mapping.keys())
    except Exception as e:
        logging.error(f"Failed to initialize applications: {str(e)}")
        raise

"""
Load the OpenMetadata configuration file while protecting sensitive information.
Avoids logging sensitive data like JWT tokens and passwords while still
providing visibility into the configuration structure.
Returns the configuration dictionary.
"""
def load_config(config_file):
    config_path = os.path.join(CONFIG_DIR, config_file)
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            safe_keys = [k for k in config.keys() if k not in ['jwt_token', 'password']]
            logging.info(f"Loaded configuration with keys: {safe_keys}")
            return config
    except Exception as e:
        logging.error(f"Error loading config file {config_file}")
        raise

"""
Retrieve all tables associated with an application from OpenMetadata.
Uses the OpenMetadata API to fetch tables based on the provided service,
database, and schema information from the application mapping.
Returns a list of dictionaries containing table information.
"""
def get_tables_for_application(base_url: str, headers: Dict, app_mapping: Dict) -> List[Dict]:
    matched_tables = []
    schema_fqn = f"{app_mapping['service']}.{app_mapping['database']}.{app_mapping['schema']}"
    endpoint = f"{base_url}/v1/tables"
    params = {
        'databaseSchema': schema_fqn,
        'fields': 'tags,name,fullyQualifiedName,version',  # Explicitly request tags
        'include': 'all',  # Include all fields
        'limit': 1000
    }
    
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        data = response.json().get('data', [])
        
        for table in data:
            table_info = {
                'table_name': table.get('name'),
                'full_fqn': table.get('fullyQualifiedName'),
                'tags': table.get('tags', [])
            }
            matched_tables.append(table_info)
        
        logging.info(f"Found {len(data)} tables in schema {schema_fqn}")
        
    except Exception as e:
        logging.error(f"Error fetching tables for schema {schema_fqn}: {str(e)}")
    
    return matched_tables

"""
Check tag status
"""
def check_tag_status(base_url, headers, table_fqn, tag_fqn):
    encoded_fqn = requests.utils.quote(table_fqn)
    response = requests.get(f"{base_url}/v1/tables/name/{encoded_fqn}", headers=headers)
    
    if response.status_code == 200:
        table_data = response.json()
        existing_tags = table_data.get('tags', [])
        return any(tag.get('tagFQN') == tag_fqn for tag in existing_tags)
    
    logging.error(f"Failed to get table data. Status code: {response.status_code}")
    return False

"""
Check if a tag exists in OpenMetadata.
Verifies that the tag is properly configured before attempting to use it.
Returns boolean indicating if tag exists.
"""
def check_tag_exists(base_url: str, headers: Dict, tag_fqn: str, dry_run: bool = True) -> bool:
    try:
        encoded_fqn = requests.utils.quote(tag_fqn)
        response = requests.get(f"{base_url}/v1/tags/name/{encoded_fqn}", headers=headers)
        
        if response.status_code == 200:
            if dry_run:
                logging.info(f"DRY RUN: Tag '{tag_fqn}' exists in OpenMetadata")
            else:
                logging.info(f"Tag '{tag_fqn}' exists in OpenMetadata")
            return True
        elif response.status_code == 404:
            if dry_run:
                logging.error(f"DRY RUN: Tag '{tag_fqn}' does not exist in OpenMetadata")
            else:
                logging.error(f"Tag '{tag_fqn}' does not exist in OpenMetadata")
            return False
        else:
            if dry_run:
                logging.error(f"DRY RUN: Error checking tag '{tag_fqn}'. Status code: {response.status_code}")
            else:
                logging.error(f"Error checking tag '{tag_fqn}'. Status code: {response.status_code}")
            return False
            
    except Exception as e:
        if dry_run:
            logging.error(f"DRY RUN: Error checking tag existence for '{tag_fqn}': {str(e)}")
        else:
            logging.error(f"Error checking tag existence for '{tag_fqn}': {str(e)}")
        return False
    
"""
Apply a tag to a specific table in OpenMetadata.
Handles both dry-run and actual tag application, including checking
current tags and updating them via the OpenMetadata API.
Returns boolean indicating success of operation.
"""
def apply_tag(base_url, headers, table_fqn, tag_fqn, dry_run=True):
    """
    Apply a tag to a specific table in OpenMetadata using PATCH method.
    """
    try:
        # First check if tag already exists on table
        encoded_fqn = requests.utils.quote(table_fqn)
        url = f"{base_url}/v1/tables/name/{encoded_fqn}"
        
        # Check current table tags
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            table_data = response.json()
            existing_tags = table_data.get('tags', [])
            if any(tag.get('tagFQN') == tag_fqn for tag in existing_tags):
                if dry_run:
                    logging.info(f"DRY RUN: Tag {tag_fqn} already exists on table {table_fqn}, skipping")
                else:
                    logging.info(f"Tag {tag_fqn} already exists on table {table_fqn}, skipping")
                return True

        if dry_run:
            logging.info(f"DRY RUN: Would apply tag {tag_fqn} to table {table_fqn}")
            return True
        
        patch_operation = [
            {
                "op": "add",
                "path": "/tags/-",
                "value": {"tagFQN": tag_fqn}
            }
        ]

        patch_headers = headers.copy()
        patch_headers['Content-Type'] = 'application/json-patch+json'

        patch_response = requests.patch(url, headers=patch_headers, json=patch_operation)
        
        if patch_response.status_code == 200:
            logging.info(f"Successfully tagged table {table_fqn} with {tag_fqn}")
            return True
        else:
            logging.error(f"Failed to tag table {table_fqn}: {patch_response.status_code}")
            if patch_response.text:
                logging.error(f"Error details: {patch_response.text}")
            return False
            
    except Exception as e:
        logging.error(f"Error applying tag to {table_fqn}: {str(e)}")
        return False

"""
Process a list of tables and apply tags as needed.
Tracks statistics about the tagging process including counts of
already tagged tables, newly tagged tables, and failed operations.
Returns a dictionary of statistics about the operation.
"""
def process_tables(openmetadata_tables, base_url, headers, tag_fqn, dry_run=True):
    """
    Process a list of tables and apply tags as needed, skipping already tagged tables.
    """
    stats = {
        'total_tables': len(openmetadata_tables),
        'already_tagged': 0,
        'newly_tagged': 0,
        'failed_tagging': 0
    }
    
    for table in openmetadata_tables:
        # First check if table already has the tag from the initial data
        if any(tag.get('tagFQN') == tag_fqn for tag in table.get('tags', [])):
            stats['already_tagged'] += 1
            logging.info(f"{'DRY RUN: ' if dry_run else ''}Table {table['full_fqn']} already has tag {tag_fqn}, skipping")
            continue
            
        # Get fresh data for the table to ensure we have latest tags
        encoded_fqn = requests.utils.quote(table['full_fqn'])
        url = f"{base_url}/v1/tables/name/{encoded_fqn}?fields=tags&include=all"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                table_data = response.json()
                current_tags = table_data.get('tags', [])
                
                # Double check if table has the tag
                if any(tag.get('tagFQN') == tag_fqn for tag in current_tags):
                    stats['already_tagged'] += 1
                    logging.info(f"{'DRY RUN: ' if dry_run else ''}Table {table['full_fqn']} already has tag {tag_fqn}, skipping")
                    continue
                
                # Only attempt to apply tag if it's not already present
                if apply_tag(base_url, headers, table['full_fqn'], tag_fqn, dry_run):
                    stats['newly_tagged'] += 1
                else:
                    stats['failed_tagging'] += 1
            else:
                logging.error(f"Failed to get table data for {table['full_fqn']}")
                stats['failed_tagging'] += 1
                
        except Exception as e:
            logging.error(f"Error processing table {table['full_fqn']}: {str(e)}")
            stats['failed_tagging'] += 1
    
    return stats

"""
Log the results of the tagging operation for a specific application.
Provides a summary of the operation including total tables processed,
number of tables already tagged, newly tagged, and failed operations.
"""
def log_tagging_results(stats, application, dry_run=True):
    run_type = "DRY RUN" if dry_run else "LIVE RUN"
    
    logging.info("\n" + "="*50)
    logging.info(f"Tagging Results for {application} ({run_type}):")
    logging.info(f"Total tables processed: {stats['total_tables']}")
    logging.info(f"Already tagged: {stats['already_tagged']}")
    logging.info(f"Newly tagged: {stats['newly_tagged']}")
    logging.info(f"Failed tagging: {stats['failed_tagging']}")

"""
Main execution function that orchestrates the entire tagging process.
Handles argument parsing, configuration loading, and iterating through
applications to process their tables and apply tags as needed.
"""
def main():
    # Setup logging first
    setup_logging()
    
    try:
        # Load application mapping and initialize applications list
        APPLICATION_NAME_MAPPING, APPLICATIONS = initialize_applications()
        
        # Set up argument parser
        parser = argparse.ArgumentParser(description='Check and tag tables in OpenMetadata.')
        parser.add_argument('--dry-run', action='store_true', help='Perform a dry run without applying tags')
        parser.add_argument('--application', choices=APPLICATIONS, help='Specific application to process')
        args = parser.parse_args()
        
        # Load configuration
        config = load_config('openmetadata_config.json')
        base_url = config['base_url']
        headers = {
            "Authorization": f"Bearer {config['jwt_token']}",
            "Content-Type": "application/json"
        }
        
        # Determine which applications to process
        applications_to_process = [args.application] if args.application else APPLICATIONS
        
        # Track overall statistics
        overall_stats = {
            'processed_apps': 0,
            'skipped_apps': 0,
            'missing_tags': [],
            'total_tables_processed': 0,
            'total_tables_tagged': 0,
            'total_tables_skipped': 0
        }
        
        for application in applications_to_process:
            logging.info(f"\nProcessing application: {application}")
            
            app_mapping = APPLICATION_NAME_MAPPING.get(application)
            if not app_mapping:
                logging.error(f"No mapping found for application: {application}")
                overall_stats['skipped_apps'] += 1
                continue
            
            # Check if tag exists before processing tables
            tag_fqn = f"Application System.{app_mapping['tag_name']}"
            if not check_tag_exists(base_url, headers, tag_fqn):
                logging.error(f"Skipping application '{application}' due to missing tag: {tag_fqn}")
                overall_stats['skipped_apps'] += 1
                overall_stats['missing_tags'].append({
                    'application': application,
                    'tag_fqn': tag_fqn
                })
                continue
            
            # Get tables from OpenMetadata API
            openmetadata_tables = get_tables_for_application(base_url, headers, app_mapping)
            
            if not openmetadata_tables:
                logging.warning(f"No tables found for application {application}")
                overall_stats['skipped_apps'] += 1
                continue
            
            # Process and tag tables
            stats = process_tables(
                openmetadata_tables,
                base_url,
                headers,
                tag_fqn,
                args.dry_run
            )
            
            # Update overall statistics
            overall_stats['processed_apps'] += 1
            overall_stats['total_tables_processed'] += stats['total_tables']
            overall_stats['total_tables_tagged'] += stats['newly_tagged']
            overall_stats['total_tables_skipped'] += stats['failed_tagging']
            
            # Log results for this application
            log_tagging_results(stats, application, args.dry_run)
        
        # Log overall summary
        logging.info("\n" + "="*50)
        logging.info("OVERALL SUMMARY:")
        logging.info(f"Applications Processed Successfully: {overall_stats['processed_apps']}")
        logging.info(f"Applications Skipped: {overall_stats['skipped_apps']}")
        if overall_stats['missing_tags']:
            logging.info("\nMissing Tags:")
            for missing in overall_stats['missing_tags']:
                logging.info(f"  - Application: {missing['application']}")
                logging.info(f"    Missing Tag: {missing['tag_fqn']}")
        logging.info(f"\nTotal Tables Processed: {overall_stats['total_tables_processed']}")
        logging.info(f"Total Tables Tagged: {overall_stats['total_tables_tagged']}")
        logging.info(f"Total Tables Skipped: {overall_stats['total_tables_skipped']}")
        logging.info("="*50 + "\n")
        
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()