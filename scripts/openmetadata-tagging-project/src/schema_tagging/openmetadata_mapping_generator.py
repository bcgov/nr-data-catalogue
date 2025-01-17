import pandas as pd
import json
import logging
from collections import defaultdict
from datetime import datetime
import os
import sys

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

# Debug print statements
print(f"Script Path: {SCRIPT_PATH}")
print(f"Script Directory: {SCRIPT_DIR}")
print(f"Src Directory: {SRC_DIR}")
print(f"Project Root: {PROJECT_ROOT}")
print(f"Data Directory: {DATA_DIR}")

def setup_logging():
    """Set up basic logging to both file and console"""
    log_file = os.path.join(LOGS_DIR, 'mapping_generator.log')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logging.info(f"=== New Mapping Generation Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

def generate_mapping_from_csv(csv_path):
    """Generate application mapping structure from CSV FQNs"""
    logging.info(f"Reading from: {csv_path}")
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at: {csv_path}")
    
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Dictionary to store unique service/database/schema combinations
    combinations = defaultdict(set)
    
    # Process each FQN
    for _, row in df.iterrows():
        fqn = row['fqn']
        parts = fqn.split('.')
        
        if len(parts) >= 4:
            service = parts[0]
            database = parts[1]
            schema = parts[2]
            
            # Create a key that combines all three elements
            key = f"{service}.{database}.{schema}"
            combinations[key].add(fqn)
    
    # Create the mapping structure
    mapping = {}
    
    for key, fqns in combinations.items():
        service, database, schema = key.split('.')
        
        app_name = f"{schema.upper()} - {database}"
        
        mapping[app_name] = {
            'tag_name': app_name,
            'service': service,
            'database': database,
            'schema': schema,
            'sample_tables': list(sorted(fqns))[:5],
            'total_tables': len(fqns)
        }
    
    return mapping

def save_mapping(mapping, output_file):
    """Save a simplified version of the mapping to a JSON file"""
    simplified_mapping = {}
    
    for app_name in sorted(mapping.keys()):
        details = mapping[app_name]
        simplified_mapping[app_name] = {
            'tag_name': details['tag_name'],
            'service': details['service'],
            'database': details['database'],
            'schema': details['schema']
        }
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(simplified_mapping, f, indent=4)
    
    logging.info(f"Mapping saved to: {output_file}")

def main():
    try:
        # Set up logging
        setup_logging()
        
        # Construct paths relative to the project root
        csv_path = os.path.join(DATA_DIR, 'openmetadata_table_fqns.csv')
        output_file = os.path.join(DATA_DIR, 'application_mapping.json')
        
        # Debug path information
        print(f"Project Root: {PROJECT_ROOT}")
        print(f"Data Directory: {DATA_DIR}")
        print(f"Looking for CSV at: {csv_path}")
        
        # Generate mapping
        mapping = generate_mapping_from_csv(csv_path)
        
        # Log discoveries
        logging.info("\nDiscovered Application Mappings:")
        for app_name, details in mapping.items():
            logging.info(f"\nApplication: {app_name}")
            logging.info(f"Service: {details['service']}")
            logging.info(f"Database: {details['database']}")
            logging.info(f"Schema: {details['schema']}")
            logging.info(f"Total Tables: {details['total_tables']}")
            logging.info("Sample Tables:")
            for fqn in details['sample_tables']:
                logging.info(f"  - {fqn}")
        
        # Save mapping
        save_mapping(mapping, output_file)
        
        # Print example usage
        print("\nExample Python structure for your application:")
        print("\nAPPLICATION_NAME_MAPPING = {")
        for app_name, details in mapping.items():
            print(f"    '{app_name}': {{")
            print(f"        'tag_name': '{details['tag_name']}',")
            print(f"        'service': '{details['service']}',")
            print(f"        'database': '{details['database']}',")
            print(f"        'schema': '{details['schema']}'")
            print("    },")
        print("}")
        
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()

# '''
# Script that interacts with OpenMetadata's API to generate a JSON mapping between applications and their database 
# locations. It identifies applications by searching for 'Application System.' tags on database tables, then captures 
# the service, database, and schema information for each application. This mapping helps teams understand where 
# different applications store their data across the database infrastructure.

# The output will have to be edited to remove any data with '_replication' and closely looked over for any other anomolies.
# '''


# import requests
# import logging
# import json
# from typing import Dict, Any
# import sys
# import os

# # def setup_logging():
# #     """Set up logging configuration"""
# #     logging.basicConfig(
# #         level=logging.INFO,
# #         format='%(asctime)s - %(levelname)s - %(message)s',
# #         handlers=[
# #             logging.StreamHandler(sys.stdout),
# #             logging.FileHandler('mapping_generator.log')
# #         ]
# #     )

# # Get the absolute path to the script itself
# SCRIPT_PATH = os.path.abspath(__file__)
# # Get the script's directory
# SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
# # Get the src directory
# SRC_DIR = os.path.dirname(SCRIPT_DIR)
# # Get the project root (parent of src)
# PROJECT_ROOT = os.path.dirname(SRC_DIR)
# # Get the config directory
# CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')
# # Get the logs directory
# LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')

# def setup_logging():
#     """Set up logging configuration"""
#     # Create logs directory if it doesn't exist
#     os.makedirs(LOGS_DIR, exist_ok=True)
#     log_file = os.path.join(LOGS_DIR, 'mapping_generator.log')
    
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(levelname)s - %(message)s',
#         handlers=[
#             logging.StreamHandler(sys.stdout),
#             logging.FileHandler(log_file)
#         ]
#     )

# def get_all_tags(base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
#     """Get all tags from OpenMetadata"""
#     try:
#         logging.info("Fetching all tags...")
#         response = requests.get(f"{base_url}/v1/tags", headers=headers)
        
#         if response.status_code == 200:
#             tags = response.json()
#             tag_count = len(tags.get('data', []))
#             logging.info(f"Found {tag_count} total tags")
            
#             # Log all tag categories found
#             categories = set()
#             for tag in tags.get('data', []):
#                 if 'category' in tag:
#                     categories.add(tag['category'])
#             logging.info(f"Found tag categories: {list(categories)}")
            
#             return tags
#         else:
#             logging.error(f"Failed to fetch tags. Status code: {response.status_code}")
#             logging.error(f"Response: {response.text}")
#             return {}
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Request failed: {str(e)}")
#         return {}

# def get_tables_for_service(base_url: str, headers: Dict[str, str], service_name: str, service_id: str) -> list:
#     """Get all tables for a given service"""
#     tables = []
#     try:
#         logging.info(f"Fetching tables for service: {service_name}")
#         response = requests.get(f"{base_url}/v1/tables?service={service_id}", headers=headers)
        
#         if response.status_code == 200:
#             data = response.json()
#             tables = data.get('data', [])
#             logging.info(f"Found {len(tables)} tables for service {service_name}")
            
#             # Log sample of table names
#             sample_tables = [table['name'] for table in tables[:5]]
#             if sample_tables:
#                 logging.info(f"Sample tables: {sample_tables}")
                
#             # Log tags found on tables
#             tags_found = set()
#             for table in tables:
#                 for tag in table.get('tags', []):
#                     tags_found.add(tag.get('tagFQN', ''))
#             if tags_found:
#                 logging.info(f"Tags found on tables: {list(tags_found)}")
#             else:
#                 logging.info("No tags found on any tables")
                
#         else:
#             logging.error(f"Failed to fetch tables. Status code: {response.status_code}")
#             logging.error(f"Response: {response.text}")
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Request failed: {str(e)}")
    
#     return tables

# def build_application_mapping(base_url: str, headers: Dict[str, str]) -> Dict[str, Dict[str, str]]:
#     """Build the APPLICATION_NAME_MAPPING dictionary from OpenMetadata"""
#     mapping = {}
    
#     # Get all tags first to understand what's available
#     all_tags = get_all_tags(base_url, headers)
    
#     # Get all database services
#     logging.info("Fetching database services...")
#     services_response = requests.get(f"{base_url}/v1/services/databaseServices", headers=headers)
    
#     if services_response.status_code != 200:
#         logging.error("Failed to fetch database services")
#         return mapping
    
#     services = services_response.json().get('data', [])
#     logging.info(f"Processing {len(services)} database services")
    
#     # Process each service
#     for service in services:
#         service_name = service['name']
#         service_id = service['id']
#         logging.info(f"\nProcessing service: {service_name}")
        
#         # Get all tables for this service
#         tables = get_tables_for_service(base_url, headers, service_name, service_id)
        
#         # Process tables
#         for table in tables:
#             table_name = table.get('name', '')
#             table_fqn = table.get('fullyQualifiedName', '')
#             tags = table.get('tags', [])
            
#             # Look for application tags
#             for tag in tags:
#                 tag_fqn = tag.get('tagFQN', '')
#                 if tag_fqn.startswith('Application System.'):
#                     app_name = tag_fqn.replace('Application System.', '')
#                     logging.info(f"Found application tag: {app_name} on table: {table_name}")
                    
#                     # Extract database and schema from FQN
#                     fqn_parts = table_fqn.split('.')
#                     if len(fqn_parts) >= 3:
#                         database = fqn_parts[1]
#                         schema = fqn_parts[2]
                        
#                         if app_name not in mapping:
#                             mapping[app_name] = {
#                                 'tag_name': app_name,
#                                 'service': service_name,
#                                 'database': database,
#                                 'schema': schema
#                             }
#                             logging.info(f"Added mapping for application: {app_name}")
    
#     logging.info(f"\nFinal mapping contains {len(mapping)} applications")
#     if mapping:
#         logging.info("Found applications: " + ', '.join(mapping.keys()))
#     else:
#         logging.warning("No application mappings were found!")
#         logging.info("Please verify that:")
#         logging.info("1. Your tables have tags starting with 'Application System.'")
#         logging.info("2. The tags are properly applied to tables")
#         logging.info("3. You have permission to view the tags")
    
#     return mapping

# # if __name__ == "__main__":
# #     import argparse
# #     from config_loader import load_config

# #     parser = argparse.ArgumentParser(description='Generate OpenMetadata application mapping.')
# #     parser.add_argument('--output', type=str, help='Output file for mapping (JSON)', default='application_mapping.json')
# #     parser.add_argument('--base-url', type=str, help='Override base URL from config')
# #     args = parser.parse_args()

# #     setup_logging()

# #     try:
# #         config = load_config('openmetadata_config.json')
# #         base_url = args.base_url if args.base_url else config['base_url']
# #         base_url = base_url.rstrip('/')
        
# #         headers = {
# #             "Authorization": f"Bearer {config['jwt_token']}",
# #             "Content-Type": "application/json"
# #         }
        
# #         mapping = build_application_mapping(base_url, headers)
        
# #         with open(args.output, 'w') as f:
# #             json.dump(mapping, f, indent=2)
            
# #     except Exception as e:
# #         logging.error(f"Error generating mapping: {str(e)}")
# #         raise

# if __name__ == "__main__":
#     import argparse
#     from config_loader import load_config

#     parser = argparse.ArgumentParser(description='Generate OpenMetadata application mapping.')
#     parser.add_argument('--output', type=str, help='Output file for mapping (JSON)', default='application_mapping.json')
#     parser.add_argument('--base-url', type=str, help='Override base URL from config')
#     args = parser.parse_args()

#     setup_logging()

#     try:
#         # Load config from the config directory
#         config = load_config(os.path.join(CONFIG_DIR, 'openmetadata_config.json'))
#         base_url = args.base_url if args.base_url else config['base_url']
#         base_url = base_url.rstrip('/')
        
#         headers = {
#             "Authorization": f"Bearer {config['jwt_token']}",
#             "Content-Type": "application/json"
#         }
        
#         mapping = build_application_mapping(base_url, headers)
        
#         # Write output to the config directory
#         output_path = os.path.join(CONFIG_DIR, args.output)
#         with open(output_path, 'w') as f:
#             json.dump(mapping, f, indent=2)
#         logging.info(f"Mapping written to: {output_path}")
            
#     except Exception as e:
#         logging.error(f"Error generating mapping: {str(e)}")
#         raise