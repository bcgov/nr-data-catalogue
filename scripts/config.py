# Configuration File
import pandas as pd
import numpy as np
import json
import os
import requests
import time
import logging
import glob
from datetime import datetime
from dotenv import load_dotenv


env = 'test' # dev or test

# API base URL TEST ENV
base_url = f"https://nr-data-catalogue-{env}.apps.emerald.devops.gov.bc.ca/api/v1"

# Database schema to filter by
database_schema = f"ODS.ods{env}.ats_replication"

# Selected user ID (replace with actual user ID)
selected_user_id = "your_user_id_here"


# Load environment variables from .env
load_dotenv()


# # API keys for each environment
# api_keys = {
#     'dev': os.getenv('API_KEY_DEV'),
#     'test': os.getenv('API_KEY_TEST'),
# }

# Get the API key for the current environment
api_key = os.getenv(f"api_key_{env}")

# Print the values for verification (optional)
print(f"Environment: {env}")
print(f"Base URL: {base_url}")

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