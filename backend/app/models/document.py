from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class DocumentChunk(BaseModel):
    chunk_id: str
    doc_id: str
    doc_title: str
    category: str
    chunk_index: int
    text: str
    embedding: Optional[List[float]] = None
    created_at: datetime

class KnowledgeDocCreate(BaseModel):
    title: str = Field(..., min_length=3)
    category: str = "General Troubleshooting"  # Database, API, Auth, Deployment, Performance, Microservices, Runbook
    content: str = Field(..., min_length=20)
    source_filename: Optional[str] = "manual_entry.txt"

class KnowledgeDocResponse(BaseModel):
    id: str
    title: str
    category: str
    source_filename: str
    content_preview: str
    total_chunks: int
    created_at: datetime

class RetrievedEvidenceItem(BaseModel):
    doc_id: str
    doc_title: str
    category: str
    relevance_score: float  # Cosine similarity score between 0.0 and 1.0
    relevance_rating: str  # High, Medium, Low
    matched_snippet: str
    chunk_index: int
