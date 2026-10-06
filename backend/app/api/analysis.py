from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from datetime import datetime, timezone

from app.core.database import get_db_collection
from app.services.rag_pipeline import ManualRAGPipeline
from app.services.timeline_generator import TimelineGenerator
from app.services.incident_analyzer import IncidentAnalyzer
from app.models.incident import AnalysisResult, IncidentStatus

router = APIRouter()

@router.post("/{incident_id}/analyze")
async def analyze_incident_endpoint(incident_id: str):
    """
    RAG-POWERED INCIDENT INVESTIGATION WORKFLOW:
    1. Fetches incident telemetry, logs, and evidence.
    2. Generates query vector & executes Vector Similarity Search on Knowledge Base.
    3. Searches for historical incidents with similar failure patterns.
    4. Reconstructs evidence-based chronological timeline.
    5. Injects retrieved context + evidence into Safety-Grounded LLM Prompt.
    6. Produces structured Root Cause Hypothesis, Confidence, Steps, and Resolution.
    7. Persists analysis into incident record.
    """
    incidents_col = get_db_collection("incidents")
    doc = await incidents_col.find_one({"$or": [{"id": incident_id}, {"incident_id": incident_id}]})
    if not doc:
        raise HTTPException(status_code=404, detail="Incident not found.")

    # 1. Build rich semantic query string for RAG retrieval
    search_query = f"{doc.get('title', '')} {doc.get('incident_type', '')} {doc.get('description', '')} {doc.get('error_messages', '')}"

    # 2. Vector search relevant runbooks and troubleshooting guides
    retrieved_knowledge = await ManualRAGPipeline.search_relevant_knowledge(search_query, top_k=4)

    # 3. Cross-reference similar past incidents
    similar_incidents = await ManualRAGPipeline.search_similar_past_incidents(
        search_query,
        current_incident_id=doc.get("incident_id"),
        top_k=2
    )

    # 4. Construct Timeline
    timeline_events = TimelineGenerator.generate_timeline(
        logs=doc.get("logs", ""),
        recent_deployment=doc.get("recent_deployment", ""),
        metrics=doc.get("metrics", ""),
        error_messages=doc.get("error_messages", ""),
        incident_description=doc.get("description", "")
    )

    # 5. Execute AI Root Cause Analysis
    analysis_result = await IncidentAnalyzer.analyze_incident(
        incident=doc,
        retrieved_docs=retrieved_knowledge,
        similar_incidents=similar_incidents
    )

    # 6. Persist to MongoDB
    timeline_dict = [t.model_dump() for t in timeline_events]
    analysis_dict = analysis_result.model_dump()

    await incidents_col.update_one(
        {"_id": doc["_id"]},
        {
            "$set": {
                "analysis": analysis_dict,
                "timeline": timeline_dict,
                "status": IncidentStatus.INVESTIGATING.value,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

    return {
        "incident_id": doc.get("incident_id"),
        "analysis": analysis_result,
        "timeline": timeline_events,
        "retrieved_evidence": retrieved_knowledge,
        "similar_incidents": similar_incidents
    }
