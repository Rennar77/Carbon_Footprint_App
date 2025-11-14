from pydantic import BaseModel
from typing import Optional

class CarLog(BaseModel):
    vehicle_id: int
    distance_km: float

class ElectricityLog(BaseModel):
    kwh: float
    region: str

class FlightLog(BaseModel):
    distance_km: float
    class_type: str
