import requests
from requests.auth import HTTPBasicAuth

USERNAME = "renar"
PASSWORD = "Renard@2025"
uid = "H4E50J1ZSSN2"

# Newer CarbonKit-compatible endpoint format
url = f"https://api.carbonkit.net/3.6/definition/{uid}"

headers = {
    "Accept": "application/json"
}

response = requests.get(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), headers=headers)
print(response.status_code)
print(response.text)
