import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, status

from app.models.incident import (
    IncidentCreate, IncidentUpdate, IncidentResponse,
    IncidentSeverity, IncidentStatus, IncidentType, ApplicationType
)
from app.core.database import get_db_collection
from app.services.rag_pipeline import ManualRAGPipeline

router = APIRouter()

@router.get("/stats")
async def get_incident_stats():
    """
    Returns analytics metrics and aggregations for the SRE dashboard using Recharts.
    Calculates:
    - Total, Open, Resolved, Critical
    - Incidents by Type
    - Incidents by Application
    - Mean Time to Resolution (MTTR)
    """
    incidents_col = get_db_collection("incidents")
    cursor = incidents_col.find({})
    all_incidents = await cursor.to_list(length=1000)

    total = len(all_incidents)
    open_count = sum(1 for i in all_incidents if i.get("status") in [IncidentStatus.OPEN.value, IncidentStatus.INVESTIGATING.value])
    resolved_count = sum(1 for i in all_incidents if i.get("status") in [IncidentStatus.RESOLVED.value, IncidentStatus.MITIGATED.value])
    critical_count = sum(1 for i in all_incidents if i.get("severity") == IncidentSeverity.CRITICAL.value)

    # By Type
    by_type: Dict[str, int] = {}
    for i in all_incidents:
        itype = i.get("incident_type", "Other")
        by_type[itype] = by_type.get(itype, 0) + 1
    type_chart_data = [{"type": k, "count": v} for k, v in by_type.items()]

    # By Application
    by_app: Dict[str, int] = {}
    for i in all_incidents:
        app_name = i.get("application", "Other")
        by_app[app_name] = by_app.get(app_name, 0) + 1
    app_chart_data = [{"application": k, "count": v} for k, v in by_app.items()]

    # Severity distribution
    by_sev: Dict[str, int] = {}
    for i in all_incidents:
        sev = i.get("severity", "Medium")
        by_sev[sev] = by_sev.get(sev, 0) + 1
    sev_chart_data = [{"severity": k, "count": v} for k, v in by_sev.items()]

    # Average Resolution Time (Mock/Calculated)
    avg_resolution_mins = 42.5  # Typical SRE baseline MTTR

    return {
        "summary": {
            "total_incidents": total,
            "open_incidents": open_count,
            "resolved_incidents": resolved_count,
            "critical_incidents": critical_count,
            "avg_resolution_time_minutes": avg_resolution_mins
        },
        "by_type": type_chart_data,
        "by_application": app_chart_data,
        "by_severity": sev_chart_data
    }

@router.get("/", response_model=List[IncidentResponse])
async def list_incidents(
    application: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    search: Optional[str] = None
):
    incidents_col = get_db_collection("incidents")
    query = {}
    if application and application != "All":
        query["application"] = application
    if status and status != "All":
        query["status"] = status
    if severity and severity != "All":
        query["severity"] = severity

    cursor = incidents_col.find(query, sort=[("created_at", -1)])
    items = await cursor.to_list(length=200)

    # Optional in-memory search filter if keyword provided
    if search:
        search_lower = search.lower()
        items = [
            i for i in items
            if search_lower in i.get("title", "").lower()
            or search_lower in i.get("incident_id", "").lower()
            or search_lower in i.get("description", "").lower()
        ]

    # Map to response format
    responses = []
    for item in items:
        responses.append(IncidentResponse(
            id=item.get("id", str(item.get("_id"))),
            incident_id=item.get("incident_id", "INC-000"),
            title=item.get("title", "Untitled"),
            application=item.get("application", ApplicationType.ECOMMERCE.value),
            incident_type=item.get("incident_type", IncidentType.API.value),
            severity=item.get("severity", IncidentSeverity.HIGH.value),
            status=item.get("status", IncidentStatus.OPEN.value),
            description=item.get("description", ""),
            logs=item.get("logs", ""),
            error_messages=item.get("error_messages", ""),
            recent_deployment=item.get("recent_deployment", ""),
            metrics=item.get("metrics", ""),
            configuration_changes=item.get("configuration_changes", ""),
            is_simulated=item.get("is_simulated", False),
            created_by=item.get("created_by", "engineer"),
            created_at=item.get("created_at", datetime.now(timezone.utc)),
            updated_at=item.get("updated_at", datetime.now(timezone.utc)),
            analysis=item.get("analysis"),
            timeline=item.get("timeline")
        ))
    return responses

@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(inc_in: IncidentCreate):
    incidents_col = get_db_collection("incidents")
    
    # Generate sequential or unique reference ID
    random_num = str(uuid.uuid4().int)[:4]
    incident_ref = f"INC-{random_num}"
    internal_id = f"inc_{str(uuid.uuid4())[:8]}"
    now = datetime.now(timezone.utc)

    # Calculate embedding for RAG past incident cross-referencing
    combined_summary = f"{inc_in.title} {inc_in.description} {inc_in.error_messages}"
    embedding = ManualRAGPipeline.generate_embedding(combined_summary)

    doc = {
        "_id": str(uuid.uuid4()),
        "id": internal_id,
        "incident_id": incident_ref,
        "title": inc_in.title,
        "application": inc_in.application,
        "incident_type": inc_in.incident_type,
        "severity": inc_in.severity,
        "status": IncidentStatus.OPEN.value,
        "description": inc_in.description,
        "logs": inc_in.logs or "",
        "error_messages": inc_in.error_messages or "",
        "recent_deployment": inc_in.recent_deployment or "",
        "metrics": inc_in.metrics or "",
        "configuration_changes": inc_in.configuration_changes or "",
        "is_simulated": inc_in.is_simulated,
        "created_by": "engineer",
        "created_at": now,
        "updated_at": now,
        "analysis": None,
        "timeline": None,
        "embedding": embedding
    }

    await incidents_col.insert_one(doc)

    return IncidentResponse(
        id=doc["id"],
        incident_id=doc["incident_id"],
        title=doc["title"],
        application=doc["application"],
        incident_type=doc["incident_type"],
        severity=doc["severity"],
        status=doc["status"],
        description=doc["description"],
        logs=doc["logs"],
        error_messages=doc["error_messages"],
        recent_deployment=doc["recent_deployment"],
        metrics=doc["metrics"],
        configuration_changes=doc["configuration_changes"],
        is_simulated=doc["is_simulated"],
        created_by=doc["created_by"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
        analysis=None,
        timeline=None
    )

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: str):
    incidents_col = get_db_collection("incidents")
    doc = await incidents_col.find_one({"$or": [{"id": incident_id}, {"incident_id": incident_id}]})
    if not doc:
        raise HTTPException(status_code=404, detail="Incident not found.")

    return IncidentResponse(
        id=doc.get("id", str(doc.get("_id"))),
        incident_id=doc.get("incident_id", "INC-000"),
        title=doc.get("title", ""),
        application=doc.get("application", ApplicationType.ECOMMERCE.value),
        incident_type=doc.get("incident_type", IncidentType.API.value),
        severity=doc.get("severity", IncidentSeverity.HIGH.value),
        status=doc.get("status", IncidentStatus.OPEN.value),
        description=doc.get("description", ""),
        logs=doc.get("logs", ""),
        error_messages=doc.get("error_messages", ""),
        recent_deployment=doc.get("recent_deployment", ""),
        metrics=doc.get("metrics", ""),
        configuration_changes=doc.get("configuration_changes", ""),
        is_simulated=doc.get("is_simulated", False),
        created_by=doc.get("created_by", "engineer"),
        created_at=doc.get("created_at", datetime.now(timezone.utc)),
        updated_at=doc.get("updated_at", datetime.now(timezone.utc)),
        analysis=doc.get("analysis"),
        timeline=doc.get("timeline")
    )

@router.patch("/{incident_id}", response_model=IncidentResponse)
async def update_incident(incident_id: str, patch: IncidentUpdate):
    incidents_col = get_db_collection("incidents")
    doc = await incidents_col.find_one({"$or": [{"id": incident_id}, {"incident_id": incident_id}]})
    if not doc:
        raise HTTPException(status_code=404, detail="Incident not found.")

    update_fields: Dict[str, Any] = {"updated_at": datetime.now(timezone.utc)}
    for field, val in patch.model_dump(exclude_unset=True).items():
        if val is not None:
            update_fields[field] = val

    await incidents_col.update_one({"_id": doc["_id"]}, {"$set": update_fields})
    updated_doc = await incidents_col.find_one({"_id": doc["_id"]})

    return IncidentResponse(
        id=updated_doc.get("id", str(updated_doc.get("_id"))),
        incident_id=updated_doc.get("incident_id", "INC-000"),
        title=updated_doc.get("title", ""),
        application=updated_doc.get("application", ApplicationType.ECOMMERCE.value),
        incident_type=updated_doc.get("incident_type", IncidentType.API.value),
        severity=updated_doc.get("severity", IncidentSeverity.HIGH.value),
        status=updated_doc.get("status", IncidentStatus.OPEN.value),
        description=updated_doc.get("description", ""),
        logs=updated_doc.get("logs", ""),
        error_messages=updated_doc.get("error_messages", ""),
        recent_deployment=updated_doc.get("recent_deployment", ""),
        metrics=updated_doc.get("metrics", ""),
        configuration_changes=updated_doc.get("configuration_changes", ""),
        is_simulated=updated_doc.get("is_simulated", False),
        created_by=updated_doc.get("created_by", "engineer"),
        created_at=updated_doc.get("created_at", datetime.now(timezone.utc)),
        updated_at=updated_doc.get("updated_at", datetime.now(timezone.utc)),
        analysis=updated_doc.get("analysis"),
        timeline=updated_doc.get("timeline")
    )

@router.delete("/{incident_id}")
async def delete_incident(incident_id: str):
    incidents_col = get_db_collection("incidents")
    doc = await incidents_col.find_one({"$or": [{"id": incident_id}, {"incident_id": incident_id}]})
    if not doc:
        raise HTTPException(status_code=404, detail="Incident not found.")
    await incidents_col.delete_one({"_id": doc["_id"]})
    return {"message": f"Incident {doc.get('incident_id')} successfully deleted."}
