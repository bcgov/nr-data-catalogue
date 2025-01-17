# OpenMetadata Tagging Project

This script is used to tag assets in OpenMetadata with an app tag by using the fully qualified name (FQN) in OpenMetadata with a list returned from the SQL script which queries the ER Studio database. If a match is found a tag is applied to the asset to link it to an application. The script has a `--dry-run` option to test before making changes to OpenMetadata.

## Folder Structure
```
   openmetadata-tagging-project/
   ├─ .env.example
   ├─ .gitignore
   ├─ README.md
   ├─ config/
   │  ├─ asset_ownership_er_studio.sql
   │  └─ openmetadata_config.json.example
   ├─ data/
   │  └─ <csv and other data will generate here>
   ├─ docs/
   │  └─ DEVELOPMENT.md
   ├─ logs/
   │  └─ <log files will generate here>
   ├─ src/
   │  ├─ __init__.py
   │  ├─ db_connection_cx.py
   │  ├─ fetch_openmetadata_fqns.py
   │  ├─ main.py
   │  ├─ openmetadata_table_list_processor.py
   │  ├─ schema_tagging/
   │  │  ├─ __init__.py
   │  │  ├─ clean_mapping_names.py
   │  │  ├─ config_loader.py
   │  │  ├─ consep_schema_tagger.py   
   │  │  ├─ openmetadata_mapping_generator.py
   │  │  └─ schema_based_omd_tagger.py
   │  └─ fta_tagging/
   │     └─ fta_tagger_csv.py
   └─ tests/
      └─ test_main.py
```

## Features

- Applies tags to OpenMetadata tables based on application ownership
- Supports a `--dry-run` mode for testing
- Includes error handling and retry logic for network issues

## Prerequisites

- Python 3.8.10
- Required Python packages (refer to a requirements.txt or pipfile)
- Access to OpenMetadata instance
- Necessary permissions and credentials for OpenMetadata and Oracle database

## Installation

### Steps to set up the project outside of a development environment:

1. Clone the repository
   ```
   git clone https://github.com/yourusername/openmetadata-tagging-project.git
   cd openmetadata-tagging-project
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt`
   ```

3. Set up configuration files
    `.env` (see .env.example) contains Oracle credentials and other configuration.
    `.openmetadata_config.json` (see openmetadata_config.json.example) contains the OpenMetadata URL and JWT Token.


### Steps to set up the project using PIPENV:

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/openmetadata-tagging-project.git
   cd openmetadata-tagging-project
   ```

2. Ensure you have pipenv installed:
   ```
   pip install pipenv
   ```

3. Install dependencies using pipenv:
   ```
   pipenv install
   ```

4. Activate the pipenv shell:
   ```
   pipenv shell
   ```

5. Set up configuration files:
    `.env` (see .env.example) contains Oracle credentials and other configuration. This file belongs in the route of the folder.
    `.openmetadata_config.json` (see openmetadata_config.json.example) contains the OpenMetadata URL and JWT Token.

## Usage

First run `fetch_openmetadata_fqns.py` to generate the csv file that will be required for the main script.

```
python src/fetch_openmetadata_fqns.py
```

After activating the pipenv shell:

- To run in dry-run mode:
  ```
  python src/main.py --dry-run
  ```

- To apply tags:
  ```
  python src/main.py
  ```

## Configuration

- OpenMetadata API endpoint can be obtained from Data Foundations once the user has been given access and then endpoint can then be added to the openmetadata_config.json file
- JWT token can be obtained from user profile in OpenMetadata under the 'Access Token' tab and added to the openmetadata_config.json file
- Database connection details can be obtained from Data Foundations if a proxy exists, otherwises a service request will have to go to DBA's

## Testing

To run the unit test use the following:
    ```
    python -m unittest discover tests
    ```

The `using unittest.mock.patch` mocks external dependencies (like API calls) so the functions can be tested in isolation.
Each test method (`test_check_table_exists`, `test_apply_tag`, `test_process_table_batch`) is testing a specific function from `main.py`.
In each test, it's setting up a scenario (like mocking an API response), calling the function being tested, and then asserting that the result matches what was expected.

The `self.assertTrue()`, `self.assertFalse()`, and `self.assertEqual()` are assertions that check if the results match the expectations.

## License

      Licensed under the Apache License, Version 2.0 (the "License");
      you may not use this file except in compliance with the License.
      You may obtain a copy of the License at

            http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
      See the License for the specific language governing permissions and
      limitations under the License.

## Acknowledgements

- [OpenMetadata Slack channel](https://openmetadata.slack.com/archives/C02B6955S4S)
- [OpenMetadata Swagger API documentation](https://docs.open-metadata.org/swagger.html)