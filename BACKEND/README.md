## 🌍 Carbon Footprint App (Backend)

This is the backend service for the Carbon Footprint App.
It allows users to estimate their carbon emissions (e.g., from transport, energy use, etc.) using the Climatiq API
.

The backend is built with FastAPI (Python) and will eventually connect to a Supabase database for user management, tracking, and analytics.

## 🚀 Features

Health Check Endpoint – Root / endpoint returns a welcome message.

Carbon Footprint Estimation – /calculate-footprint endpoint integrates with Climatiq’s API to return estimated emissions.

Configurable with .env – Keeps API keys safe and out of code.

Modular Structure – Prepared for routers (e.g., carbon.py, users.py).

## 📂 Project Structure
```
Carbon_Footprint_App/
│
└── BACKEND/
    ├── app/
    │   ├── main.py            # FastAPI entry point
    │   ├── __init__.py        # Makes app a Python package
    │   └── routers/           # (future) separate API routes
    │
    ├── test/
    │   ├── test_carbon_api.py # Test script for Climatiq
    │   └── list_activities.py # Query emission factors
    │
    ├── requirements.txt       # Python dependencies
    └── .env                   # Environment variables (not in Git)
```

## ⚙️ Installation

# Clone the repo:
```
git clone https://github.com/Rennar77/carbon-footprint-app.git
cd carbon-footprint-app/BACKEND
```

# Create & activate a virtual environment:
```
python -m venv venv
venv\Scripts\activate   # on Windows
source venv/bin/activate  # on Mac/Linux
```

 # Install dependencies:
 ```
pip install -r requirements.txt
```

Create a .env file in BACKEND/ and add your Climatiq API key:
```
CLIMATIQ_API_KEY=your_api_key_here
```
# ▶️ Running the Backend

From the BACKEND folder:
```
uvicorn app.main:app --reload
```

The API will be available at:
👉 http://127.0.0.1:8000

Interactive API docs:
👉 http://127.0.0.1:8000/docs

# 🧪 Example Request
```
POST /calculate-footprint

Request body:

{
  "activity_id": "passenger_vehicle-vehicle_type_car-fuel_source_na-distance_na-engine_size_na",
  "activity_value": 10,
  "activity_unit": "passenger-km",
  "data_version": "25.25"
}


Response:

{
  "co2e": 0.75,
  "co2e_unit": "kg",
  "emission_factor": {
    "name": "Average passenger car average distance",
    "source": "ADEME",
    "year": 2021
  }
}
```
# 📦 Requirements (requirements.txt)
```
fastapi==0.115.0
uvicorn[standard]==0.30.6
python-dotenv==1.0.1
requests==2.32.3
```

