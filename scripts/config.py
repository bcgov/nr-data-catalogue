# Configuration File

import requests

# API base URL
base_url = "https://nr-data-catalogue-dev.apps.emerald.devops.gov.bc.ca/api/v1"

# Database schema to filter by
database_schema = "ODS.odsdev.lexis_replication"

# API key for authentication
api_key = "eyJraWQiOiJHYjM4OWEtOWY3Ni1nZGpzLWE5MmotMDI0MmJrOTQzNTYiLCJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJvcGVuLW1ldGFkYXRhLm9yZyIsInN1YiI6Imphc3RpbmRlci5hdGh3YWwiLCJyb2xlcyI6WyJBZG1pbiJdLCJlbWFpbCI6Imphc3RpbmRlci5hdGh3YWxAZ292LmJjLmNhIiwiaXNCb3QiOmZhbHNlLCJ0b2tlblR5cGUiOiJQRVJTT05BTF9BQ0NFU1MiLCJpYXQiOjE3MjM4NDA1MjcsImV4cCI6MTczMTYxNjUyN30.NJefOnWXXILxawFKwNadMsNpYW6soUMwBFrokKg1vBuBESHCim1Tz5oU-dKrw2KxkwW4X0pgldiPbiyPXj8iRbxhQAeCUClWq6c984p20nvB0j9Mldj3YlNudLrKOCi-fIQk-oxhhhs4LcG6-zoiO3nyCgsWBnFJ2aheJUVPTfKb2irbuYWfExfTXPKF3_Q9A2FWDROXg5bOAsvOifNq7knkBk0Rlbf051ZSPhrQfkI3PKgRn6yoE8E5rb7WsH2nYlIg7jkl1TIINsjUg3wK5CGiu8arOKwGuznYorGSVmOwaMmP1carbEvsHr2H4zC-74HNmrncyXRkOB6C4jt4YA"

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
