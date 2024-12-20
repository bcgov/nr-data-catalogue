from config import *

#Schema Method - list all tables in a schema

# Endpoint for retrieving tables filtered by database schema, set a high limit to get them all
endpoint1 = f"/tables?databaseSchema={database_schema}&limit=9999"

# Full URL
url = base_url + endpoint1

# Make the GET request to retrieve tables
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


# Iterate over each table ID and remove the tag
for table_id in table_id_list:
    # Endpoint for updating a table
    endpoint2 = f"/tables/{table_id}"

    # Full URL
    url = base_url + endpoint2

    # Data payload for removing the table tags
    data = [
        {
            "op": "remove",  # Use "remove" to delete the tag
            "path": "/tags",  # Specify the path to the tags
            "value": [
                {
                    "tagFQN": "Test Classification.Ignore this tag"  
                }
            ]
        }
    ]

    # Make the PATCH request
    response = requests.patch(url, headers=headers_patch, json=data)

    # Check the response status
    if response.status_code == 200:
        print(f"Tag removed from table {table_id} successfully!")
        #print(response.json())
    else:
        print(f"Failed to remove tag from table {table_id}: {response.status_code}")
        print(response.text) 
    time.sleep(2)

# Finally, tag the schema itself
endpoint3 = f"/schemas/{database_schema}"  # Assuming database_schema is the fully qualified name (FQN)
url = base_url + endpoint3

response = requests.patch(url, headers=headers_patch, json=data)

if response.status_code == 200:
    print(f"Tag removed to schema {database_schema} successfully!")
else:
    print(f"Failed to remove tag to schema {database_schema}: {response.status_code}")
    print(response.text)