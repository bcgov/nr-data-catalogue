# OpenMetadata - Batch Processing Scripts


## Overview
This project is designed to interact with APIs, process data, and assign tags or ownership to tables. The scripts fetch table data, process classifications, and log outputs for transparency and debugging.

## Folder Structure
- **`reference_csvs/`**: Folder containing CSV files used as input data for batch processing.
- **`users/`**: Folder for scripts pertaining to adding/removing users to data assets in the data catalog.
- **`tags/`**: Folder for scripts pertaining to applying or uploading tags to the catalogue.
- **`config.py`**: Configuration file for setting up API connections and project settings.

## Requirements
To run the project, ensure the following dependencies are installed. Use a `requirements.txt` file for easy setup.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/bcgov/nr-data-catalogue.git
   cd project
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```


### API Keys
Store API keys securely and load them dynamically based on the environment.

1. Use `.env` File:
   - Create a `.env` file in the project directory:
     ```plaintext
     api_key_dev=your_dev_api_key_here
     api_key_test=your_test_api_key_here
     ```
   - Add `.env` to `.gitignore` to avoid exposing sensitive data.

2. Update `config.py`:
   ```python
   from dotenv import load_dotenv
   import os

   # Load environment variables
   load_dotenv()

   env = 'test'  # Set to 'dev' or 'test'

   api_key = os.getenv(f"api_key_{env}")
   base_url = f"https://nr-data-catalogue-{env}.apps.emerald.devops.gov.bc.ca/api/v1"
   ```

### Log Files
- Log files are saved in the `tests` folder.
- Filenames include timestamps for easy identification.


### Fetch All Tables
Run the script to fetch all table data, including columns and their tags:
```bash
python fetch_all_tables_columns.py
```
- The data will be saved as a CSV file in the `tests` folder.
- Progress is logged in the terminal and a log file.

## Error Handling (In progress)
- All API responses are logged for debugging.
- Failures are written to log files for review.
- Ensure API endpoints and keys are correct to avoid errors.

## Contributing
1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request.

## License
This project is licensed under the MIT License. See `LICENSE` for details.