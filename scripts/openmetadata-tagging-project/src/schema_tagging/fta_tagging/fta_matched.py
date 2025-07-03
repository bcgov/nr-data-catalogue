# Script to compare dbq01_the_schema.csv against both erstudio_fta.csv (tables and views)
# Matches OBJECT_NAME from DBQ01 to TABLE_NAME in files
# Outputs matching TABLE_NAME and APPLICATION pairs

# Script to compare dbq01_the_schema.csv against both erstudio_fta.csv (tables and views)
# Matches OBJECT_NAME from DBQ01 to TABLE_NAME in files
# Outputs matching TABLE_NAME and APPLICATION pairs

import pandas as pd
import os

# Get the absolute path to the script itself
SCRIPT_PATH = os.path.abspath(__file__)
# Get the script's directory (fta_tagging)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
# Get schema_tagging directory
SCHEMA_DIR = os.path.dirname(SCRIPT_DIR)
# Get src directory
SRC_DIR = os.path.dirname(SCHEMA_DIR)
# Get the project root (parent of src)
PROJECT_ROOT = os.path.dirname(SRC_DIR)
# Define other directory paths
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')

def merge_fta_files():
    # File paths
    dbq_file = os.path.join(DATA_DIR, 'THE_schema_dump.csv')
    erstudio_file = os.path.join(DATA_DIR, 'er_studio_fta_tables_views.csv')
    output_file = os.path.join(DATA_DIR, 'matched_records_fta.csv')
    
    # Read files
    dbq = pd.read_csv(dbq_file)
    erstudio = pd.read_csv(erstudio_file)
    
    # Rename column in dbq to match erstudio's TABLE_NAME
    dbq = dbq.rename(columns={'OBJECT_NAME': 'TABLE_NAME'})
    
    # Drop OBJECT_TYPE column from dbq
    dbq = dbq.drop(columns=['OBJECT_TYPE'])
    
    # Drop ASSET_TYPE column from erstudio
    erstudio = erstudio.drop(columns=['ASSET_TYPE'])
    
    # Merge on TABLE_NAME
    merged_results = pd.merge(dbq, erstudio, on='TABLE_NAME', how='inner', suffixes=('_dbq', '_erstudio'))
    
    # Remove duplicates if any exist
    final_results = merged_results.drop_duplicates(subset=['TABLE_NAME'])
    
    # Save results
    final_results.to_csv(output_file, index=False)
    print(f"Total unique matches: {len(final_results)}")
    print("\nSample of matched records:")
    print(final_results.head())
    
    return final_results

if __name__ == '__main__':
    merge_fta_files()