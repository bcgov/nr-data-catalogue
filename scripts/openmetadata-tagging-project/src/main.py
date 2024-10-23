# This script does the following:
# 
# 1. clears the log file at the start of each run and adds a timestamp to each log entry.
# 2. checks for the existence of tags but does not create missing tags.
# 3. applies existing tags to tables using the PATCH method.
# 4. processes tables in batches with a delay between batches to avoid overwhelming the API.
# 5. provides a comprehensive summary at the end of the run.
#
# To use this script, you'll need to ensure you have the following in place:
#
# 1. A openmetadata_config.json file with your base_url and jwt_token.
# 2. A openmetadata_table_fqns.csv file with the table FQNs.
# 3. An sql file with your SQL query.
# 4. The db_connection_cx module for database connections.
# 5. The openmetadata_table_list_processor module with the load_openmetadata_tables function.

import os
import json
import pandas as pd
from db_connection_cx import get_db_connection
import logging
import requests
from typing import List, Dict
import time
from datetime import datetime
from requests.exceptions import RequestException
import sys
import argparse
import socket
from urllib.parse import urlparse

# Import the function to load OpenMetadata tables
from openmetadata_table_list_processor import load_openmetadata_tables

# List of applications
APPLICATION_LIST = [
    'ACAT', 'ACS', 'APT2', 'AQHI', 'ARIS', 'ARIS_WHSE', 'ARS', 'ATA', 'ATS', 'BCEMAP', 'BCTS_SPATIAL', 'BEC', 'CAMP', 'CBBA_WHSE',
    'CBM', 'CCLRMP_WHSE', 'CCSD', 'CEF', 'CFSWEB', 'CI', 'CIRRAS', 'CIRRAS_CCCS', 'CIRRAS_LEGACY', 'CLIENT', 'CMS', 'CONSEP',
    'CORP_PERSON_ORG', 'CRISP', 'CRSRA', 'CSAT', 'CSP', 'CWB_WHSE', 'CWM', 'DISRMS', 'EDAB', 'EIRS', 'ELDS', 'ERA', 'ESF', 'ESRITOOL',
    'EUL', 'FAM_Model', 'FARM', 'FFS', 'FNIRS', 'FPCT', 'FSA_CLIENT', 'FSP', 'FTC', 'GATOR', 'GBA', 'GBMS', 'GEOMARK', 'GWELLS', 'ILCR',
    'IRS', 'ISDUT', 'ITVR', 'ITVR', 'LEXIS', 'LINKNET', 'LTRACK', 'MALS', 'MPNA', 'MSD', 'MTEC', 'NOTICES', 'NSA2', 'OATS', 'OCERS', 'OSS',
    'PAR', 'PASO', 'PEFP', 'PPS', 'PSCIS', 'RDBD', 'REC', 'REFERRAL', 'REPREPO', 'REPT', 'RESPROJ', 'RMS', 'RTM', 'SCS', 'SDR', 'SOSS', 'TR',
    'TSADMRPT', 'TUS', 'VMAD', 'VRIMS', 'WF1_ORG', 'WIMSI'
]

BATCH_SIZE = 100
BATCH_DELAY = 2  # seconds

def check_dns(url, timeout=5):
    """Check if the hostname in the URL can be resolved."""
    try:
        hostname = urlparse(url).netloc
        socket.gethostbyname(hostname)
        return True
    except socket.error:
        return False

def retry_with_backoff(func, max_retries=5, initial_delay=1, backoff_factor=2):
    """Retry a function with exponential backoff."""
    def wrapper(*args, **kwargs):
        delay = initial_delay
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except RequestException as e:
                if attempt == max_retries - 1:
                    raise
                logging.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= backoff_factor
    return wrapper

def execute_sql_query(query, engine, params=None):
    try:
        df = pd.read_sql(query, engine, params=params)
        return df
    except Exception as e:
        logging.error(f"Error executing SQL query: {str(e)}")
        raise

def load_config(config_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    config_path = os.path.join(project_root, 'config', config_name)
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

@retry_with_backoff
def check_table_exists(base_url, headers, table_fqn):
    encoded_fqn = requests.utils.quote(table_fqn)
    response = requests.get(f"{base_url}/v1/tables/name/{encoded_fqn}", headers=headers)
    return response.status_code == 200

@retry_with_backoff
def check_tag_exists(base_url, headers, tag_fqn):
    encoded_fqn = requests.utils.quote(tag_fqn)
    response = requests.get(f"{base_url}/v1/tags/name/{encoded_fqn}", headers=headers)
    return response.status_code == 200

@retry_with_backoff
def apply_tag(base_url, headers, table_fqn, tag_fqn, dry_run=False):
    encoded_fqn = requests.utils.quote(table_fqn)
    url = f"{base_url}/v1/tables/name/{encoded_fqn}"
    
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

    # Log the exact payload and headers we're sending
    logging.info(f"Sending PATCH request to {url}")
    logging.info(f"Headers: {patch_headers}")
    logging.info(f"Payload: {json.dumps(patch_operation)}")

    # Apply the PATCH operation
    patch_response = requests.patch(url, headers=patch_headers, json=patch_operation)
    patch_response.raise_for_status()
    
    logging.info(f"Successfully applied tag '{tag_fqn}' to table '{table_fqn}'")
    return True

def process_table_batch(base_url, headers, tables, tag_fqn, tag_exists, dry_run=False):
    existing_tables = 0
    missing_tables = 0
    tag_applications = 0
    failed_tag_applications = 0

    for table_name, table_info in tables:
        try:
            if check_table_exists(base_url, headers, table_info['fqn']):
                existing_tables += 1
                logging.info(f"Table found in OpenMetadata: {table_info['fqn']}")
                
                if tag_exists:
                    if apply_tag(base_url, headers, table_info['fqn'], tag_fqn, dry_run):
                        tag_applications += 1
                    else:
                        failed_tag_applications += 1
            else:
                logging.warning(f"Table in list but not found in OpenMetadata API: {table_info['fqn']}")
                missing_tables += 1
        except RequestException as e:
            logging.error(f"Failed to process table {table_info['fqn']}: {str(e)}")
            failed_tag_applications += 1

    return existing_tables, missing_tables, tag_applications, failed_tag_applications

class DatePrefixFormatter(logging.Formatter):
    def format(self, record):
        record.asctime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return super().format(record)

def setup_logging():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    log_file = os.path.join(project_root, 'logs', 'openmetadata_tagging_run.log')
    
    # Ensure the logs directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Set up logging with date prefix
    formatter = DatePrefixFormatter('%(asctime)s - %(levelname)s - %(message)s')

    # Set up file handler for logging to file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Set up stream handler for logging to console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Configure the root logger
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(file_handler)
    logging.getLogger().addHandler(console_handler)

    # Add a date header for this run
    run_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"--- New Run Started at {run_date} ---")

def main():
    parser = argparse.ArgumentParser(description='Apply tags to tables in OpenMetadata.')
    parser.add_argument('--dry-run', action='store_true', help='Perform a dry run without applying tags')
    args = parser.parse_args()

    setup_logging()

    if args.dry_run:
        logging.info("Running in DRY RUN mode. No changes will be applied.")

    try:
        config = load_config('openmetadata_config.json')
        
        base_url = config['base_url']
        jwt_token = config['jwt_token']
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }

        # Check DNS resolution before starting
        if not check_dns(base_url):
            logging.error(f"Unable to resolve hostname for {base_url}. Please check your network connection and DNS settings.")
            return

        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        csv_path = os.path.join(project_root, 'data', 'openmetadata_table_fqns.csv')
        openmetadata_tables = load_openmetadata_tables(csv_path)

        engine = get_db_connection()
        sql_file_path = os.path.join(project_root, 'config', 'asset_ownership_er_studio.sql')
        with open(sql_file_path, 'r') as file:
            base_sql_query = file.read()

        total_applications_processed = 0
        total_tables = 0
        total_existing_tables = 0
        total_missing_tables = 0
        existing_tags = 0
        missing_tags = 0
        total_tag_applications = 0
        total_failed_tag_applications = 0

        for application in APPLICATION_LIST:
            logging.info(f"Processing application: {application}")
            sql_query = base_sql_query.replace("({application})", ":application")
            df = execute_sql_query(sql_query, engine, params={"application": application})

            tag_fqn = f"Application System.{application}"
            tag_exists = check_tag_exists(base_url, headers, tag_fqn)
            if tag_exists:
                existing_tags += 1
                logging.info(f"Tag '{tag_fqn}' exists in OpenMetadata.")
            else:
                missing_tags += 1
                logging.warning(f"Tag '{tag_fqn}' does not exist in OpenMetadata.")

            if 'table_name' in df.columns:
                tables = [(table_name, openmetadata_tables.get(table_name.lower())) 
                          for table_name in df['table_name'] if table_name.lower() in openmetadata_tables]
                total_tables += len(tables)

                # Process tables in batches
                for i in range(0, len(tables), BATCH_SIZE):
                    batch = tables[i:i+BATCH_SIZE]
                    existing, missing, applied, failed = process_table_batch(base_url, headers, batch, tag_fqn, tag_exists, args.dry_run)
                    total_existing_tables += existing
                    total_missing_tables += missing
                    total_tag_applications += applied
                    total_failed_tag_applications += failed

                    if i + BATCH_SIZE < len(tables):
                        logging.info(f"Waiting {BATCH_DELAY} seconds before processing next batch...")
                        time.sleep(BATCH_DELAY)

            total_applications_processed += 1
            logging.info(f"Finished processing application: {application}")

        summary = f"""
        Run Summary:
        Dry Run: {'Yes' if args.dry_run else 'No'}
        Total applications processed: {total_applications_processed}
        Total tables checked: {total_tables}
        Existing tables in OpenMetadata: {total_existing_tables}
        Missing tables in OpenMetadata: {total_missing_tables}
        Existing tags in OpenMetadata: {existing_tags}
        Missing tags in OpenMetadata: {missing_tags}
        {'Simulated' if args.dry_run else 'Actual'} tag applications: {total_tag_applications}
        {'Simulated' if args.dry_run else 'Actual'} failed tag applications: {total_failed_tag_applications}
        """
        logging.info(summary)

    except Exception as e:
        logging.error(f"An error occurred in the main script: {str(e)}")
    finally:
        if 'engine' in locals():
            engine.dispose()
            logging.info("Database connection closed.")

if __name__ == "__main__":
    main()