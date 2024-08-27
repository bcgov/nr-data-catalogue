from config import *

# Endpoint for updating a given dashboard
dashboard_id = "44f38010-7c9e-4eba-9aef-6ea18ca82150"  # Replace with the actual table ID or FQN
endpoint = f"/dashboards/{dashboard_id}"

# Full URL
url = base_url + endpoint

# Data payload for updating the dashboard tags
data = [
    {
        "op": "add",  # You can use "add" or "replace" depending on whether the tag exists or not
        "path": "/tags",
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
    print("Dashboard tags updated successfully!")
    print(response.json())
else:
    print(f"Failed with status code {response.status_code}")
    print(response.text)