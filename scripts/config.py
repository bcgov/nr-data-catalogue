# Configuration File
import pandas as pd
import json
import os
import requests
import time
import logging
from datetime import datetime

env = 'test'

# API base URL TEST ENV
base_url = f"https://nr-data-catalogue-{env}.apps.emerald.devops.gov.bc.ca/api/v1"

# Database schema to filter by
database_schema = f"ODS.ods{env}.ats_replication"

# Selected user ID (replace with actual user ID)
selected_user_id = "your_user_id_here"

# API key for authentication
api_key = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6Imphc3RpbmRlci5hdGh3YWwiLCJyb2xlcyI6WyJOUk0gRGF0YSBDb25zdW1lciBSb2xlIiwiQWRtaW4iXSwiZW1haWwiOiJqYXN0aW5kZXIuYXRod2FsQGdvdi5iYy5jYSIsImlzQm90IjpmYWxzZSwidG9rZW5UeXBlIjoiUEVSU09OQUxfQUNDRVNTIiwiaWF0IjoxNzMyNzMyMDAzLCJleHAiOjE3MzUzMjQwMDN9.vz3So31Pi6IgsxLLIa-1kpQICnlccVExh9lpeDHx4TCWY2qxQ5ZzJWlc2yBh6YiwY7cozdurJ4jhwD05f9x3Xgb2cSwCwNDh_Kb0I4dvPsfONOs_a_cUm3sQV3COoQxEFYKXr78eW2lwYsDOAtAdRfINWHp_Np9lX30oLHsJgXD4E6hG6EGIb5PJJQ2TK6UuVAa5rWWD8gJ_z4CSEfAZNmYF5sSe2OJpxfsjKYrRkDYjf05jhdHM7Da-90wSPSfarXPYFQhYaXKyW7_Js9MBXEG5qvWt6rd7ps9jXz1xl3Lm1_r92sGtl8cFNmHpDJI1rMnvvp8RXXUoR9uCa5DJ2g"

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