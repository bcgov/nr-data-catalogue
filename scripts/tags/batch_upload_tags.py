from config import *

# Load your data that contains all the information needed to generate a tag
df = pd.read_csv('reference_csvs/irs.csv')

# Endpoint for creating a tag
endpoint = "/tags"
url = base_url + endpoint

# Loop through each row in the DataFrame to retrieve the information for generating a tag
for i, row in df.iterrows():
    data = {
        "classification": "Application System",  # This must be one of the classifications that exist in OpenMetaData
        "name": f"{row['APPLICATION_NAME']}",  # Tag name from the DataFrame
        "description": f"{row['TEXT']} \r\n\r\n\r\nData Model URL: {row['DATA_MODEL_URL']}",  # Description from the DataFrame
        "displayName": f"{row['FULL_NAME']}"  # Display name from the DataFrame
    }

    # Make the POST request to create the tag based on the info provided in the CSV
    response = requests.post(url, headers=headers_get, json=data)

    # Check the response status for each request
    if response.status_code == 200 or response.status_code == 201:
        print(f"Tag created successfully for row {i} - {row['APPLICATION_NAME']}!")
    else:
        print(f"Failed to create tag for row {i} with status code {response.status_code}")
        print(response.text)

    # Optional: Add a small pause between requests to avoid overwhelming the server
    time.sleep(1)