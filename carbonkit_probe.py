# carbonkit_probe.py
import requests
from requests.auth import HTTPBasicAuth
import json
import os

# ---------- CONFIG ----------
USERNAME = "renar"
PASSWORD = "Renard@2025"
BASE = "https://api.carbonkit.net/3.6"
UID = "H4E50J1ZSSN2"   # <-- replace with the uid you got from search
# -----------------------------

auth = HTTPBasicAuth(USERNAME, PASSWORD)
headers = {"Accept": "application/json", "Content-Type": "application/json"}

candidates = [
    f"{BASE}/items/{UID}",
    f"{BASE}/{UID}",
    f"{BASE}/contexts/{UID}",
    f"{BASE}/categories/{UID}",
    f"{BASE}/items;label?uid={UID}",
    f"{BASE}/search;name;label?q={UID}&types=DC,DI"
]

print("Probing endpoints for UID:", UID)
for url in candidates:
    try:
        r = requests.get(url, auth=auth, headers=headers, timeout=10)
        print("\nURL:", url)
        print("Status:", r.status_code)
        text = r.text.strip()
        print("Body sample:", (text[:1000] + '...') if len(text) > 1000 else text)
    except Exception as e:
        print("\nURL:", url)
        print("Error:", str(e))

# ---------- If you want a test calculation using the uid ----------
# NOTE: this only runs if you set DO_CALC to True below.
DO_CALC = False

if DO_CALC:
    calc_url = f"{BASE}/calculate"   # common name used historically
    payload = {
        "item": UID,
        "values": {
            "distance": 10,   # adjust depending on what the model expects
            "units.distance": "km"
        }
    }
    print("\nAttempting calculation POST ->", calc_url)
    try:
        r = requests.post(calc_url, auth=auth, headers=headers, json=payload, timeout=10)
        print("Calc status:", r.status_code)
        try:
            print("Calc JSON:", json.dumps(r.json(), indent=2) )
        except Exception:
            print("Calc body sample:", r.text[:1000])
    except Exception as e:
        print("Calc error:", str(e))
