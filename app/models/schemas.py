from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class ThreatEvent(BaseModel):
    event_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    client_ip: str
    method: str
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body: Optional[str] = None
    threat_type: str  # "SQLi", "RateLimit"
    severity: str  # "Low", "Medium", "High", "Critical"
    explanation: Optional[str] = None
    status: str = "Detected"

class LogEntry(BaseModel):
    event_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    client_ip: str
    method: str
    path: str
    status_code: int
    threat_detected: bool = False
    threat_details: Optional[ThreatEvent] = None
