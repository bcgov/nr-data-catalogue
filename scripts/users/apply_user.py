from config import *

#Schema Method - list all tables in a schema

# Endpoint for retrieving tables filtered by database schema, set a high limit to get them all
endpoint1 = f"/tables?databaseSchema={database_schema}&limit=9999"

# Full URL
url = base_url + endpoint1

# Make the GET request to retrieve all tables in the given schema
response = requests.get(url, headers=headers_get)

# Check the response status
if response.status_code == 200:
    print("Raw Response Content:", response.text)  # Print the raw content of the response
    try:
        tables = response.json().get('data', [])  # Attempt to parse JSON response
        print("Tables retrieved successfully!")
        for table in tables:
            print(f"Table Name: {table['name']}, ID: {table['id']}")
    except ValueError as e:
        print("Failed to parse JSON response:", e)
else:
    print(f"Failed to retrieve tables: {response.status_code}")
    print(response.text)

table_id_list = []
for table in tables:
    table_id_list.append(table['id'])




# Function to apply user to a table
def apply_user_to_table(table_id):
    # Endpoint for updating a table
    table_endpoint = f"/tables/{table_id}"

    # Full URL
    table_url = base_url + table_endpoint

    # Data payload for applying the user
    data = [
        {
            "op": "replace",
            "path": "/owners",
            "value": [
                {
                "id": selected_user_id,
                "type": "user"
            }
            ]
        }
    ]

    # Make the PATCH request
    response = requests.patch(table_url, headers=headers_patch, json=data)

    # Check the response status
    if response.status_code == 200:
        print(f"User applied to table {table_id} successfully!")
    else:
        print(f"Failed to apply user to table {table_id}: {response.status_code}")
        print(response.text)

# Apply user to all tables in the schema
for table in tables:
    apply_user_to_table(table['id'])
    time.sleep(1)