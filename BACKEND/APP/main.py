# BACKEND/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
CLIMATIQ_API_KEY = os.getenv("CLIMATIQ_API_KEY")
BASE_URL = "https://api.climatiq.io/data/v1/estimate"

app = FastAPI(title="Carbon Footprint API", version="1.0.0")

# Request model
class CarbonRequest(BaseModel):
    activity_id: str
    activity_value: float
    activity_unit: str
    data_version: str = "25.25"  # default to latest

@app.get("/")
def root():
    return {"message": "Welcome to the Carbon Footprint API!"}

@app.post("/calculate-footprint")
def calculate_footprint(req: CarbonRequest):
    headers = {"Authorization": f"Bearer {CLIMATIQ_API_KEY}"}
    payload = {
        "emission_factor": {
            "activity_id": req.activity_id,
            "data_version": req.data_version
        },
        "parameters": {
            "activity_value": req.activity_value,
            "activity_unit": req.activity_unit
        }
    }

    response = requests.post(BASE_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return response.json()
