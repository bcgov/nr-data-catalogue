import pandas as pd
import json
import logging
from collections import defaultdict
from datetime import datetime
import os

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