from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import requests

router = APIRouter(prefix="/v1/cooking", tags=["cooking"])

CLIMATIQ_API_KEY = os.getenv("CLIMATIQ_API_KEY")
BASE_URL = "https://api.climatiq.io/v1/estimate"


class CookingEstimateRequest(BaseModel):
    activity_id: str
    parameters: dict


@router.post("/estimate")
def estimate_cooking(req: CookingEstimateRequest):
    headers = {
        "Authorization": f"Bearer {CLIMATIQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "activity_id": req.activity_id,
        "parameters": req.parameters,
    }
    resp = requests.post(BASE_URL, headers=headers, json=payload)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.json())
    return resp.json()

