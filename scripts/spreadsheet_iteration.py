import os
import requests
import pandas as pd
import boto3

objbucket='' # find in Vault
objid='' # find in Vault
objkey='' # find in Vault
objurl='https://nrs.objectstore.gov.bc.ca'
objfile_key = 'data_classification/[file name].xlsx' # find in S3 Browser
database_schema = 'geobc+test+database.GEOTST.ats' # name of the schema being updated in Catalogue
api_token = 'Bearer ' # Use access token for OpenMetadata DEV

# Make a temporary dir to store Excel file
def create_dir():
    try:
        existing_path = os.getcwd()
        download_path = os.path.join(existing_path, "tempdir", "isc_spreadsheet.xlsx")
        print(download_path)
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        return download_path
    except Exception as e:
        raise Exception(f"Directory Error: {str(e)}")

# Call v1/tables to create a list of the tables & dictionary of columns within the schema
def call_api(database_schema, api_token):
    try:
        base_url = "https://nr-data-catalogue-dev.apps.emerald.devops.gov.bc.ca/api/v1"
        headers = {
            "Authorization": api_token,
            "Content-Type": "application/json"}
        endpoint = f"/tables?databaseSchema={database_schema}&includeEmptyTestSuite=true&limit=100&include=non-deleted"
        response = requests.get(f"{base_url}{endpoint}", headers=headers)
        if response.status_code == 200:
            api_data = response.json().get('data', [])
            if isinstance(api_data, list):
                table_list = [table['name'].lower() for table in api_data]
                print("Extracted API tables:", table_list)
                column_dict = {}
                for table in api_data:
                    table_name = table['name'].lower()
                    column_names = [column['name'].lower() for column in table['columns']]
                    column_dict[table_name] = column_names
                print("Extracted API Columns:", column_dict)
            return table_list, column_dict
    except Exception as e:
        raise Exception(f"API Error: {str(e)}")

# Download Excel file from S3
def get_s3(objbucket, objid, objkey, objurl, objfile_key, download_path):
    try:
        session = boto3.Session(aws_access_key_id=objid, aws_secret_access_key=objkey, region_name='us-east-1')
        s3_resource = session.resource('s3', endpoint_url=objurl)
        bucket = s3_resource.Bucket(objbucket)
        print(f'\nDownloading the object {objfile_key}...')
        bucket.download_file(objfile_key, download_path)
        print(f'File downloaded successfully to {download_path}')
    except Exception as e:
        raise Exception(f"S3 Error: {str(e)}")

# Filter df to keep only columns and tables that exist in OMD
def filter_df(df, table_list, column_dict):
    # Set everything to lower case to match output of api_call()
    df['Table'] = df['Table'].str.lower()
    df['Column'] = df['Column'].str.lower()
    # Remove lines in the 'df' that have tables which do not exist in output of api_call()
    filtered_df = df[df['Table'].isin(table_list)]
    # Iterate through columns to find mismatches between Excel and output of api_call()
    columns_to_keep = []
    for table_name in filtered_df['Table'].unique():
        expected_columns = column_dict.get(table_name, [])
        current_table_rows = filtered_df[filtered_df['Table'] == table_name]
        missing_columns = []
        for index, row in current_table_rows.iterrows():
            if row['Column'] not in expected_columns:
                missing_columns.append(row['Column'])
        if missing_columns:
            print(f"Table '{table_name}' is missing columns: {set(missing_columns)}")
        else:
            columns_to_keep.extend(expected_columns)
    # Remove lines in the 'df' that have columns which do not exist in output of api_call()
    filtered_df = filtered_df[filtered_df['Column'].isin(columns_to_keep)]
    return filtered_df

def main():
    table_list, column_dict = call_api(database_schema, api_token)
    download_path = create_dir()
    get_s3(objbucket, objid, objkey, objurl, objfile_key, download_path)
    df = pd.read_excel(download_path)
    filter_df(df, table_list, column_dict)

main()
