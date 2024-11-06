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
api_key = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6Imphc3RpbmRlci5hdGh3YWwiLCJyb2xlcyI6WyJOUk0gRGF0YSBDb25zdW1lciBSb2xlIiwiQWRtaW4iXSwiZW1haWwiOiJqYXN0aW5kZXIuYXRod2FsQGdvdi5iYy5jYSIsImlzQm90IjpmYWxzZSwidG9rZW5UeXBlIjoiUEVSU09OQUxfQUNDRVNTIiwiaWF0IjoxNzMwNTAxODM0LCJleHAiOjE3MzMwOTM4MzR9.kiqpKYrV1afqLLvRKI1l1d_rfEqkOBlIhhr-RHK_KHWVCRmt8iY2dIMP9BcnGMdr7wwkI8Av0hcydik0cQ9yHkwiLhDMK6_-wMID0RFqqc6Dvd_nY5l-Zy_33jJeQIAJikUxfte28EobwnMpEJN30kzJh2FN14tiOA11TQm4ccUG_B0LfNB3AlVmmgfakAEwftPaXE12KLc5tIcwJ2IlIXChwhTCacK0kATp7yk9elPjCsmRjLYpaXhDq9MBKLg66YX2pqrTV_v5UI4Axbq1zXJjoqAIWrTl5uo-cmJw7iO-E_MtT8S_1xmCA7ITEAJQXBsC1S7utiRop1NfGF7o-Q"

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