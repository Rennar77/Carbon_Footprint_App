## Backend Setup

### Prerequisites
- Python 3.10+

### Install
1. Create and activate a virtualenv
2. Install dependencies:
```
pip install -r Requirement.txt
```

### Environment
Create a `.env` file in `app/` or project root with:
```
CLIMATIQ_API_KEY=your_api_key
```

### Run
From `BACKEND/app` directory:
```
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Endpoints
- `GET /` health message
- `POST /calculate-footprint` proxy to Climatiq

