from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class IncidentSeverity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class IncidentStatus(str, Enum):
    OPEN = "Open"
    INVESTIGATING = "Investigating"
    MITIGATED = "Mitigated"
    RESOLVED = "Resolved"

class IncidentType(str, Enum):
    DATABASE = "Database"
    API = "API"
    AUTHENTICATION = "Authentication"
    PERFORMANCE = "Performance"
    DEPLOYMENT = "Deployment"
    MICROSERVICE = "Microservice"
    OTHER = "Other"

class ApplicationType(str, Enum):
    ECOMMERCE = "E-commerce"
    RIDE_BOOKING = "Ride Booking"
    COLLEGE_PORTAL = "College Portal"
    BANKING = "Banking"
    CHAT = "Chat Application"
    DELIVERY = "Delivery Application"
    OTHER = "Other System"

class IncidentEvidence(BaseModel):
    logs: Optional[str] = ""
    error_messages: Optional[str] = ""
    recent_deployment: Optional[str] = ""
    metrics: Optional[str] = ""
    configuration_changes: Optional[str] = ""

class AnalysisResult(BaseModel):
    summary: str
    probable_root_cause: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_rating: str  # High, Medium, Low
    supporting_evidence: List[str] = []
    contributing_factors: List[str] = []
    recommended_investigation_steps: List[str] = []
    suggested_resolution: str
    preventive_actions: List[str] = []
    retrieved_knowledge_sources: List[Dict[str, Any]] = []
    analyzed_at: Optional[datetime] = None

class TimelineEvent(BaseModel):
    timestamp_display: str  # E.g. "10:15 AM" or "T+15m (Inferred)"
    event: str
    source: str  # "Logs", "Deployment", "Metrics", "User Report"
    is_inferred: bool = False

class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=3)
    application: str = ApplicationType.ECOMMERCE.value
    incident_type: str = IncidentType.API.value
    severity: str = IncidentSeverity.HIGH.value
    description: str = Field(..., min_length=10)
    logs: Optional[str] = ""
    error_messages: Optional[str] = ""
    recent_deployment: Optional[str] = ""
    metrics: Optional[str] = ""
    configuration_changes: Optional[str] = ""
    is_simulated: bool = False

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    logs: Optional[str] = None
    error_messages: Optional[str] = None
    recent_deployment: Optional[str] = None
    metrics: Optional[str] = None
    configuration_changes: Optional[str] = None

class IncidentResponse(BaseModel):
    id: str
    incident_id: str  # E.g. "INC-1042"
    title: str
    application: str
    incident_type: str
    severity: str
    status: str
    description: str
    logs: Optional[str] = ""
    error_messages: Optional[str] = ""
    recent_deployment: Optional[str] = ""
    metrics: Optional[str] = ""
    configuration_changes: Optional[str] = ""
    is_simulated: bool = False
    created_by: Optional[str] = "engineer"
    created_at: datetime
    updated_at: datetime
    analysis: Optional[AnalysisResult] = None
    timeline: Optional[List[TimelineEvent]] = None
    embedding: Optional[List[float]] = None
