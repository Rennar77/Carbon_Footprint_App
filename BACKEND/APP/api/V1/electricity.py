from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import requests

router = APIRouter(prefix="/v1/electricity", tags=["electricity"])

CLIMATIQ_API_KEY = os.getenv("CLIMATIQ_API_KEY")
BASE_URL = "https://api.climatiq.io/data/v1/estimate"


class ElectricityEstimateRequest(BaseModel):
    activity_id: str
    data_version: str = "25.25"
    parameters: dict


@router.post("/estimate")
def estimate_electricity(req: ElectricityEstimateRequest):
    headers = {"Authorization": f"Bearer {CLIMATIQ_API_KEY}"}
    payload = {
        "emission_factor": {
            "activity_id": req.activity_id,
            "data_version": req.data_version,
        },
        "parameters": req.parameters,
    }
    resp = requests.post(BASE_URL, headers=headers, json=payload)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.json())
    return resp.json()

