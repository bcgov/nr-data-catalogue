'''
To use this script try:

python script.py --csv-file your_tables.csv

dry run:
python script.py --csv-file your_tables.csv --dry-run

'''
import os
import json
import logging
import requests
import pandas as pd
from typing import List, Dict
import time
from datetime import datetime
from requests.exceptions import RequestException
import sys
import argparse

# Get the absolute path to the script itself
SCRIPT_PATH = os.path.abspath(__file__)
# Get the script's directory
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
# Get the project root (3 levels up from schema_tagging directory)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
# Get the config and data directories
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')

# Debug logging to verify paths
print(f"Script Path: {SCRIPT_PATH}")
print(f"Script Directory: {SCRIPT_DIR}")
print(f"Project Root: {PROJECT_ROOT}")
print(f"Config Directory: {CONFIG_DIR}")
print(f"Data Directory: {DATA_DIR}")
print(f"Logs Directory: {LOGS_DIR}")

# Add project root to system path for imports
sys.path.append(PROJECT_ROOT)

def load_config(config_path: str = None) -> Dict:
    """
    Load configuration from the config directory.
    """
    if not config_path:
        config_path = os.path.join(CONFIG_DIR, 'openmetadata_config.json')
    
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        raise
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in configuration file: {config_path}")
        raise
    except Exception as e:
        logging.error(f"Error loading configuration: {str(e)}")
        raise

def load_tables_from_csv(csv_path: str) -> List[Dict]:
    """
    Load table information from CSV file with case-insensitive column matching.
    """
    try:
        df = pd.read_csv(csv_path)
        
        # Convert all column names to lowercase for comparison
        df.columns = df.columns.str.lower()
        
        # Define required columns and their possible variations
        required_columns = {
            'table_name': ['table_name', 'tablename', 'table', 'name'],
            'application': ['application', 'app', 'tag']
        }
        
        # Find matching columns for each required field
        column_mapping = {}
        for required_col, variations in required_columns.items():
            matching_cols = [col for col in df.columns if col.lower() in variations]
            if matching_cols:
                column_mapping[required_col] = matching_cols[0]
            else:
                available_columns = ', '.join(df.columns.tolist())
                raise ValueError(f"Could not find a column matching '{required_col}'. "
                               f"Available columns are: {available_columns}")
        
        tables = []
        for _, row in df.iterrows():
            # Construct FQN with 'the' schema
            table_info = {
                'name': row[column_mapping['table_name']],
                'fqn': f"DBQ01.DBQ01.the.{row[column_mapping['table_name']]}",
                'application': row[column_mapping['application']]
            }
            tables.append(table_info)
        
        logging.info(f"Successfully mapped columns: {column_mapping}")
        return tables
        
    except pd.errors.EmptyDataError:
        logging.error("The CSV file is empty")
        raise
    except FileNotFoundError:
        logging.error(f"CSV file not found: {csv_path}")
        raise
    except Exception as e:
        logging.error(f"Error loading CSV file: {str(e)}")
        raise

def check_table_exists(base_url: str, headers: Dict, table_fqn: str) -> tuple:
    """
    Check if table exists and return tuple of (exists, correct_fqn).
    """
    try:
        encoded_fqn = requests.utils.quote(table_fqn)
        url = f"{base_url}/v1/tables/name/{encoded_fqn}?fields=tags&include=all"
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            table_data = response.json()
            logging.info(f"Found match: {table_fqn}")
            
            # Log existing tags - they're in the root level 'tags' array
            existing_tags = table_data.get('tags', [])
            tag_fqns = [tag.get('tagFQN') for tag in existing_tags]
            logging.info(f"Current tags on table: {tag_fqns}")
            
            return True, table_fqn
            
        return False, None

    except Exception as e:
        logging.error(f"Error checking table existence: {str(e)}")
        return False, None

def check_tag_exists(base_url: str, headers: Dict, tag_fqn: str) -> bool:
    """
    Check if tag exists and log detailed info about the check.
    """
    try:
        encoded_fqn = requests.utils.quote(tag_fqn)
        url = f"{base_url}/v1/tags/name/{encoded_fqn}"
        logging.info(f"Checking tag existence: {tag_fqn} at URL: {url}")
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            logging.info(f"Tag '{tag_fqn}' exists in OpenMetadata")
            return True
        else:
            logging.error(f"Tag check failed. Status code: {response.status_code}")
            logging.error(f"Response content: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Error checking tag existence: {str(e)}")
        return False

def apply_tag(base_url: str, headers: Dict, table_fqn: str, tag_fqn: str, dry_run: bool = False) -> bool:
    """
    Apply a tag to a table.
    """
    encoded_fqn = requests.utils.quote(table_fqn)
    url = f"{base_url}/v1/tables/name/{encoded_fqn}?fields=tags&include=all"  # Added fields and include parameters
    
    try:
        # First, get the current table metadata
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        table_data = response.json()
        
        # Check if the tag is already applied
        existing_tags = table_data.get('tags', [])
        tag_fqns = [tag.get('tagFQN') for tag in existing_tags]
        logging.info(f"Found existing tags on table: {tag_fqns}")
        
        if tag_fqn in tag_fqns:
            if dry_run:
                logging.info(f"DRY RUN: Table '{table_fqn}' is already tagged with '{tag_fqn}' - skipping")
            else:
                logging.info(f"Table '{table_fqn}' is already tagged with '{tag_fqn}' - skipping")
            return True
            
        # Log when tag is not found
        logging.info(f"Tag '{tag_fqn}' not found in existing tags: {tag_fqns}")

        if dry_run:
            logging.info(f"DRY RUN: Would apply tag '{tag_fqn}' to table '{table_fqn}'")
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
        patch_url = f"{base_url}/v1/tables/name/{encoded_fqn}"  # Remove query parameters for PATCH
        patch_response = requests.patch(patch_url, headers=patch_headers, json=patch_operation)
        patch_response.raise_for_status()
        
        logging.info(f"Successfully applied tag '{tag_fqn}' to table '{table_fqn}'")
        return True

    except Exception as e:
        logging.error(f"Failed to apply tag '{tag_fqn}' to table '{table_fqn}': {str(e)}")
        if hasattr(e, 'response'):
            logging.error(f"Response status code: {e.response.status_code}")
            logging.error(f"Response content: {e.response.text}")
        return False

def process_tables(base_url: str, headers: Dict, tables: List[Dict], dry_run: bool = False) -> tuple:
    """
    Process tables in batches and apply tags.
    """
    BATCH_SIZE = 100
    BATCH_DELAY = 2  # seconds

    total_tables = len(tables)
    existing_tables = 0
    missing_tables = 0
    tag_applications = 0
    failed_tag_applications = 0

    for i in range(0, total_tables, BATCH_SIZE):
        batch = tables[i:i+BATCH_SIZE]
        
        for table in batch:
            table_fqn = table['fqn']
            tag_fqn = f"Application System.{table['application']}"

            exists, correct_fqn = check_table_exists(base_url, headers, table_fqn)
            if exists:
                existing_tables += 1
                logging.info(f"Found table: {correct_fqn}")
                
                if check_tag_exists(base_url, headers, tag_fqn):
                    if apply_tag(base_url, headers, correct_fqn, tag_fqn, dry_run):
                        tag_applications += 1
                    else:
                        failed_tag_applications += 1
                else:
                    logging.warning(f"Tag '{tag_fqn}' does not exist in OpenMetadata")
                    failed_tag_applications += 1
            else:
                logging.warning(f"Table not found in OpenMetadata: {table_fqn}")
                missing_tables += 1

        if i + BATCH_SIZE < total_tables:
            logging.info(f"Waiting {BATCH_DELAY} seconds before processing next batch...")
            time.sleep(BATCH_DELAY)

    return existing_tables, missing_tables, tag_applications, failed_tag_applications

def setup_logging(dry_run: bool = False) -> None:
    """
    Set up logging configuration to write to both file and console.
    """
    # Generate log filename with timestamp in the logs directory
    logs_dir = LOGS_DIR
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(logs_dir, f'openmetadata_tagging_fta_{timestamp}.log')
    
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

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description='OpenMetadata Table Tagging Script')
    parser.add_argument('--dry-run', action='store_true', 
                      help='Perform a dry run without applying any tags')
    parser.add_argument('--csv-file', required=True,
                      help='Path to the CSV file containing table information')
    parser.add_argument('--config', help='Path to custom config file')
    return parser.parse_args()

def main():
    args = parse_arguments()
    setup_logging(args.dry_run)

    try:
        config = load_config(args.config)
        
        base_url = config['base_url']
        jwt_token = config['jwt_token']
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }

        # Load tables from CSV
        tables = load_tables_from_csv(args.csv_file)
        logging.info(f"Loaded {len(tables)} tables from CSV file")

        # Process tables
        existing_tables, missing_tables, tag_applications, failed_tag_applications = process_tables(
            base_url, headers, tables, args.dry_run
        )

        run_type = "[DRY RUN] " if args.dry_run else ""
        summary = f"""
        {run_type}Run Summary:
        Total tables checked: {len(tables)}
        Existing tables in OpenMetadata: {existing_tables}
        Missing tables in OpenMetadata: {missing_tables}
        {"Would apply" if args.dry_run else "Applied"} tags successfully: {tag_applications}
        Failed tag applications: {failed_tag_applications}
        """
        logging.info(summary)

    except Exception as e:
        logging.error(f"An error occurred in the main script: {str(e)}")
        logging.exception("Full traceback:")
        sys.exit(1)

if __name__ == "__main__":
    main()