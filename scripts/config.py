# Configuration File
import pandas as pd
import json
import os
import requests
import time
import logging
from datetime import datetime

# API base URL TEST ENV
base_url = "https://nr-data-catalogue-test.apps.emerald.devops.gov.bc.ca/api/v1"

# Database schema to filter by
database_schema = "ODS.odsdev.ats_replication"

# Selected user ID (replace with actual user ID)
selected_user_id = "your_user_id_here"

# API key for authentication
api_key = "insert_your_token_here"
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