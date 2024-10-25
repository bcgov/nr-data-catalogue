# Usage:
# openmetadata_tables = load_openmetadata_tables('path/to/your/openmetadata_table_list.csv')

import csv

def load_openmetadata_tables(file_path):
    table_dict = {}
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header if present
        for row in reader:
            fqn = row[0]  # Assuming the FQN is in the first column
            parts = fqn.split('.')
            if len(parts) == 4:
                service, database, schema, table = parts
                table_dict[table.lower()] = {
                    'service': service,
                    'database': database,
                    'schema': schema,
                    'fqn': fqn
                }
    return table_dict