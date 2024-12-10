from config import *

# Timestamp for log file name
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_name = f"tests/log_{env}_all_table_fetch_{timestamp}.txt"

# Function to log messages
def log_message(message):
    with open(log_file_name, "a") as log_file:
        log_file.write(message + "\n")
    print(message)  # Also print to console for immediate feedback

# Function to fetch all tables in one request
def fetch_all_tables():
    log_message(f"Starting to fetch all {env} tables with their column tags...")
    response = requests.get(
        f"{base_url}/tables?limit=15000&fields=columns,tags",
        headers=headers_get
    )
    if response.status_code != 200:
        log_message(f"Failed to fetch tables: {response.status_code}")
        log_message(response.text)
        return []

    data = response.json().get("data", [])
    log_message(f"Fetched {len(data)} tables in a single request.")
    return data

# Function to display basic progress
def show_progress(current, total):
    percent = (current / total) * 100
    print(f"Progress: {current}/{total} ({percent:.2f}%)", end="\r")

# Main script
def main():
    # Fetch table data
    tables = fetch_all_tables()
    if not tables:
        log_message("No tables found. Exiting.")
        return

    # Prepare data for CSV with basic progress display
    table_rows = []
    total_tables = len(tables)
    for i, table in enumerate(tables, start=1):
        table_id = table["id"]
        table_name = table.get("fullyQualifiedName", "Unknown")
        table_tags = [tag["tagFQN"] for tag in table.get("tags", [])]

        for column in table.get("columns", []):
            column_name = column["name"]
            column_tags = [tag["tagFQN"] for tag in column.get("tags", [])]

            table_rows.append({
                "Table ID": table_id,
                "Table Name": table_name,
                "Table Tags": ", ".join(table_tags),
                "Column Name": column_name,
                "Column Tags": ", ".join(column_tags),
            })

        # Display progress
        show_progress(i, total_tables)

    # Convert to DataFrame
    df = pd.DataFrame(table_rows)

    # Save to CSV
    csv_filename = f"tests/{env}_tables_with_columns_{timestamp}.csv"
    df.to_csv(csv_filename, index=False)
    log_message(f"Table data saved to {csv_filename}.")

if __name__ == "__main__":
    main()
