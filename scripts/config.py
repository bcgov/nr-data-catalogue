# Configuration File

import requests
import time

# API base URL
base_url = "https://nr-data-catalogue-dev.apps.emerald.devops.gov.bc.ca/api/v1"

# Database schema to filter by
database_schema = "your_schema_here"

# API key for authentication
api_key = ""

# API request headers for get requests 
headers_get = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"  
}

# API request headers for patch requests
headers_patch = {
    "Content-Type": "application/json-patch+json",
    "Authorization": f"Bearer {api_key}"  
}