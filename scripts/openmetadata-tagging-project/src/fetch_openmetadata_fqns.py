import requests
import logging
import csv
import json
import time
import os
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_path: str) -> Dict:
    with open(config_path, 'r') as config_file:
        return json.load(config_file)

def get_all_table_fqns(base_url: str, headers: Dict, batch_size: int = 100) -> List[str]:
    all_fqns = []
    after = None
    while True:
        url = f"{base_url}/v1/tables?fields=fullyQualifiedName&limit={batch_size}"
        if after:
            url += f"&after={after}"
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logging.error(f"Failed to fetch tables: {response.status_code}")
            break
        
        data = response.json()
        fqns = [table.get('fullyQualifiedName') for table in data.get('data', []) if table.get('fullyQualifiedName')]
        all_fqns.extend(fqns)
        
        after = data.get('paging', {}).get('after')
        if not after:
            break
        
        logging.info(f"Fetched {len(all_fqns)} table FQNs so far. Waiting 2 seconds before next batch...")
        time.sleep(2)
    
    return all_fqns

def save_to_csv(data: List[str], filename: str):
    if not data:
        logging.warning("No data to save to CSV.")
        return
    
    with open(filename, 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(['fqn'])  # Header
        for fqn in data:
            writer.writerow([fqn])
    logging.info(f"Data saved to {filename}")

def main():
    # Get the root directory of the project
    project_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    # Load configuration
    config_path = os.path.join(project_root, 'config', 'openmetadata_config.json')
    config = load_config(config_path)
    base_url = config['base_url']
    jwt_token = config['jwt_token']
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    # Fetch all table FQNs from OpenMetadata
    all_fqns = get_all_table_fqns(base_url, headers)
    logging.info(f"Total table FQNs fetched: {len(all_fqns)}")

    # Save results to CSV
    output_file = os.path.join(project_root, 'data', 'openmetadata_table_fqns2.csv')
    save_to_csv(all_fqns, output_file)

if __name__ == "__main__":
    main()