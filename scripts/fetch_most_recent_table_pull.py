from config import *


def get_most_recent_csv(directory):
    """
    Fetch the most recent CSV file from the specified directory.
    :param directory: Path to the directory containing CSV files.
    :return: Path to the most recent CSV file, or None if no files are found.
    """
    # Get all CSV files in the directory
    csv_files = glob.glob(os.path.join(directory, "*.csv"))
    if not csv_files:
        print("No CSV files found in the directory.")
        return None

    # Find the most recent file based on modification time
    most_recent_file = max(csv_files, key=os.path.getmtime)
    print(f"Most recent CSV file: {most_recent_file}")
    return most_recent_file

def main():
    # Specify the directory where CSVs are stored
    tests_folder = "tests"

    # Get the most recent CSV file
    recent_csv = get_most_recent_csv(tests_folder)
    if recent_csv:
        print(f"Processing file: {recent_csv}")

        # Read the CSV into a DataFrame
        try:
            df = pd.read_csv(recent_csv)
            print(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns.")
            return df
        except Exception as e:
            print(f"An error occurred while reading the CSV: {e}")

if __name__ == "__main__":
    df = main()