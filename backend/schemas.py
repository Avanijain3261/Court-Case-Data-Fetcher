from pydantic import BaseModel
from typing import List, Optional

# --- NEW: Schema for a single order ---
class Order(BaseModel):
    date: str
    url: str

# --- Case Details Request Schema ---
class CaseRequest(BaseModel):
    case_type: str
    case_number: str
    case_year: str

# --- Case Details Response Schema (Updated) ---
class CaseResponse(BaseModel):
    party_names: str
    filing_date: str
    next_hearing_date: str
    orders_link: str # Added this field back
    orders: List[Order] # This now expects a list of Order objects

class ErrorResponse(BaseModel):
    detail: str