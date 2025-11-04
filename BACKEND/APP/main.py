from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services import vehicle_service 

from services import log_service, auth_service, summary_service


app = FastAPI(title="Carbon Footprint API")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow Flutter frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_service.router, prefix="/auth", tags=["Authentication"])
app.include_router(log_service.router, prefix="/log", tags=["Logging"])
app.include_router(summary_service.router, prefix="/dashboard", tags=["Summary"])
app.include_router(vehicle_service.router, prefix="/vehicles", tags=["Vehicles"])

@app.get("/")
def home():
    return {"message": "Carbon Footprint API is running 🚀"}
