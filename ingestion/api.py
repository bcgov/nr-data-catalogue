import requests
 
# Set your OpenMetadata API endpoint and authentication token
api_endpoint = 'https://nr-data-catalogue-dev.apps.emerald.devops.gov.bc.ca/api/v1'
# Obtained from the bot "ingestion-bot"
auth_token = '' # JWT is acquired from ingestion bot in the UI
 
# Example API endpoint to make a request to
api_url = f'{api_endpoint}/tags'
 
# Set up headers with the authentication token
headers = {
    'Authorization': f'Bearer {auth_token}',
    'Content-Type': 'application/json'
}
 
# Make a GET request to the API endpoint
response = requests.get(api_url, headers=headers)
 
# Check the response status code
if response.status_code == 200:
    # Request was successful, do something with the response data
    data = response.json()
    print(data)
else:
    # Request failed, print error message
    print(f'Error: {response.status_code} - {response.text}')