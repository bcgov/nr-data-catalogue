# Configuration File
import pandas as pd
import json
import os
import requests
import time
import logging
from datetime import datetime

# API base URL
base_url = "https://nr-data-catalogue-dev.apps.emerald.devops.gov.bc.ca/api/v1"

# Database schema to filter by
database_schema = "your_schema_here"

# Selected user ID (replace with actual user ID)
selected_user_id = "your_user_id_here"

# API key for authentication
api_key = "your_token_here"

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
