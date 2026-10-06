from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class PostmortemReport(BaseModel):
    id: str
    incident_id: str
    incident_ref_id: str
    title: str
    summary: str
    impact: str
    affected_system: str
    severity: str
    timeline: List[Dict[str, Any]] = []
    detection: str
    probable_root_cause: str
    evidence: List[str] = []
    contributing_factors: List[str] = []
    resolution: str
    recovery: str
    preventive_actions: List[str] = []
    lessons_learned: List[str] = []
    related_incidents: List[str] = []
    author: str = "SRE Incident Agent"
    status: str = "Draft"  # Draft, In Review, Published
    created_at: datetime
    updated_at: datetime

class PostmortemUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    impact: Optional[str] = None
    detection: Optional[str] = None
    probable_root_cause: Optional[str] = None
    evidence: Optional[List[str]] = None
    contributing_factors: Optional[List[str]] = None
    resolution: Optional[str] = None
    recovery: Optional[str] = None
    preventive_actions: Optional[List[str]] = None
    lessons_learned: Optional[List[str]] = None
    status: Optional[str] = None
