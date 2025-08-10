# backend/main.py

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json

# CORRECTED IMPORTS: Changed from relative to direct
import models
import schemas
from database import SessionLocal, engine, get_db
from scraper import fetch_case_details # Import our working scraper function

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Court Data Fetcher API")

# --- CORS Middleware ---
# This allows our React frontend (on a different port) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"], # Add Vite's port here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Court Data Fetcher API!"}

@app.post("/api/fetch-case", response_model=schemas.CaseResponse)
def api_fetch_case(request: schemas.CaseRequest, db: Session = Depends(get_db)):
    """
    The main API endpoint to fetch case data.
    """
    print(f"Received request for: {request.case_type} {request.case_number}/{request.case_year}")
    
    # Call our scraper function
    case_details = fetch_case_details(
        case_type=request.case_type,
        case_number=request.case_number,
        case_year=request.case_year
    )

    if not case_details:
        raise HTTPException(status_code=404, detail="Case not found or scraper failed. Check backend logs.")

    # --- Database Logging ---
    # Create a new log entry
    log_entry = models.QueryLog(
        case_type=request.case_type,
        case_number=request.case_number,
        case_year=request.case_year,
        parsed_response_json=json.dumps(case_details) # Store the result as a JSON string
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    print(f"Successfully logged query with ID: {log_entry.id}")

    return case_details