# NammaSpot Python Backend

FastAPI backend for the NammaSpot Android/Kivy prototype.

## Run locally (Windows)

```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs for interactive API documentation.

## API endpoints

- GET /health — health check
- GET /api/providers — list active providers; optional category, latitude, longitude and radius_km filters
- POST /api/providers — create a provider record
- POST /api/requests — create a help request
- GET /api/requests — list help requests; optional status filter
- PATCH /api/requests/{id} — update request status

The backend creates a local SQLite database named nammaspot.db automatically.

## Example: create a help request

```json
{
  "service": "Mechanic",
  "phone": "9000000000",
  "description": "Bike will not start",
  "customer_name": "Demo Customer",
  "latitude": 12.9279,
  "longitude": 79.335
}
```

## Important production work still required

This is an initial development backend, not a production-ready public service. Before public launch, add authentication and role-based authorization, OTP verification, rate limiting, input/phone validation, HTTPS deployment, backups, privacy controls and protected provider/request management. Do not expose the write endpoints publicly until authentication is implemented. Use real provider data only with permission.
