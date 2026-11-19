import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from math import radians, sin, cos, sqrt, atan2
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

APP_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("NAMMASPOT_DB", APP_DIR / "nammaspot.db"))

app = FastAPI(
    title="NammaSpot API",
    description="Backend API for nearby services and local help requests.",
    version="1.0.0",
)

# Restrict origins with NAMMASPOT_CORS_ORIGINS in production.
origins = os.getenv("NAMMASPOT_CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
)


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(connect()) as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS providers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            phone TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            address TEXT DEFAULT '',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS help_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT NOT NULL,
            description TEXT DEFAULT '',
            customer_name TEXT DEFAULT '',
            phone TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            status TEXT NOT NULL DEFAULT 'open',
            created_at TEXT NOT NULL
        );
        """)
        conn.commit()


@app.on_event("startup")
def startup():
    init_db()


class ProviderCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    category: str = Field(min_length=2, max_length=60)
    phone: str = Field(min_length=7, max_length=20)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    address: str = Field(default="", max_length=250)


class HelpRequestCreate(BaseModel):
    service: str = Field(min_length=2, max_length=80)
    phone: str = Field(min_length=7, max_length=20)
    description: str = Field(default="", max_length=1000)
    customer_name: str = Field(default="", max_length=100)
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)


class StatusUpdate(BaseModel):
    status: str = Field(pattern="^(open|accepted|completed|cancelled)$")


def row_dict(row):
    return dict(row) if row else None


def distance_km(lat1, lon1, lat2, lon2):
    radius = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return radius * 2 * atan2(sqrt(a), sqrt(1 - a))


@app.get("/")
def root():
    return {"app": "NammaSpot", "message": "API is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "database": "sqlite", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/api/providers")
def list_providers(
    category: Optional[str] = None,
    latitude: Optional[float] = Query(default=None, ge=-90, le=90),
    longitude: Optional[float] = Query(default=None, ge=-180, le=180),
    radius_km: float = Query(default=25, gt=0, le=500),
):
    if (latitude is None) != (longitude is None):
        raise HTTPException(400, "Provide both latitude and longitude.")
    with closing(connect()) as conn:
        if category:
            rows = conn.execute(
                "SELECT * FROM providers WHERE is_active=1 AND lower(category)=lower(?)",
                (category,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM providers WHERE is_active=1").fetchall()

    providers = [row_dict(row) for row in rows]
    if latitude is not None:
        for provider in providers:
            provider["distance_km"] = round(
                distance_km(latitude, longitude, provider["latitude"], provider["longitude"]), 2
            )
        providers = [p for p in providers if p["distance_km"] <= radius_km]
        providers.sort(key=lambda p: p["distance_km"])
    return {"count": len(providers), "providers": providers}


@app.post("/api/providers", status_code=201)
def create_provider(data: ProviderCreate):
    now = datetime.now(timezone.utc).isoformat()
    with closing(connect()) as conn:
        cur = conn.execute(
            """INSERT INTO providers
            (name, category, phone, latitude, longitude, address, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (data.name, data.category, data.phone, data.latitude, data.longitude, data.address, now),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM providers WHERE id=?", (cur.lastrowid,)).fetchone()
    return row_dict(row)


@app.post("/api/requests", status_code=201)
def create_help_request(data: HelpRequestCreate):
    if (data.latitude is None) != (data.longitude is None):
        raise HTTPException(400, "Provide both latitude and longitude.")
    now = datetime.now(timezone.utc).isoformat()
    with closing(connect()) as conn:
        cur = conn.execute(
            """INSERT INTO help_requests
            (service, description, customer_name, phone, latitude, longitude, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (data.service, data.description, data.customer_name, data.phone,
             data.latitude, data.longitude, now),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM help_requests WHERE id=?", (cur.lastrowid,)).fetchone()
    return row_dict(row)


@app.get("/api/requests")
def list_help_requests(status: Optional[str] = None):
    with closing(connect()) as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM help_requests WHERE status=? ORDER BY id DESC", (status,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM help_requests ORDER BY id DESC").fetchall()
    return {"count": len(rows), "requests": [row_dict(row) for row in rows]}


@app.patch("/api/requests/{request_id}")
def update_request_status(request_id: int, data: StatusUpdate):
    with closing(connect()) as conn:
        cur = conn.execute(
            "UPDATE help_requests SET status=? WHERE id=?", (data.status, request_id)
        )
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(404, "Help request not found.")
        row = conn.execute("SELECT * FROM help_requests WHERE id=?", (request_id,)).fetchone()
    return row_dict(row)
