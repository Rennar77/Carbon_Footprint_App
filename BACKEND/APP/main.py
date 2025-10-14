# BACKEND/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
CLIMATIQ_API_KEY = os.getenv("CLIMATIQ_API_KEY")
BASE_URL = "https://api.climatiq.io/data/v1/estimate"

app = FastAPI(title="Carbon Footprint API", version="1.1.0")

# Allow all origins for development; tighten for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include versioned routers
from app.api.V1.trips import router as trips_router
from app.api.V1.cooking import router as cooking_router
from app.api.V1.electricity import router as electricity_router

app.include_router(trips_router)
app.include_router(cooking_router)
app.include_router(electricity_router)

# Request model
class CarbonRequest(BaseModel):
    activity_id: str
    data_version: str = "25.25"  # default to latest
    parameters: dict   # allow any valid parameter structure

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
        "parameters": req.parameters
    }

    response = requests.post(BASE_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return response.json()
