# backend/models.py

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    case_type = Column(String, index=True)
    case_number = Column(String, index=True)
    case_year = Column(String, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    # We will store the successful parsed response as a JSON string
    parsed_response_json = Column(Text, nullable=True) 