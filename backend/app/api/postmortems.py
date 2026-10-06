from fastapi import APIRouter, HTTPException, status, Response
from typing import List, Optional
from datetime import datetime, timezone

from app.models.postmortem import PostmortemReport, PostmortemUpdate
from app.models.incident import AnalysisResult, TimelineEvent
from app.core.database import get_db_collection
from app.services.postmortem_generator import PostmortemGenerator

router = APIRouter()

@router.post("/{incident_id}/generate", response_model=PostmortemReport)
async def generate_postmortem_endpoint(incident_id: str):
    """
    POSTMORTEM GENERATOR:
    Translates raw incident data, AI investigation hypothesis, timeline, and impact
    into a structured, industry-standard blameless Postmortem document.
    """
    incidents_col = get_db_collection("incidents")
    doc = await incidents_col.find_one({"$or": [{"id": incident_id}, {"incident_id": incident_id}]})
    if not doc:
        raise HTTPException(status_code=404, detail="Incident not found.")

    if not doc.get("analysis"):
        raise HTTPException(
            status_code=400,
            detail="Incident has not been analyzed yet. Please run AI Analysis before generating a postmortem."
        )

    # Reconstruct Pydantic models from stored dicts
    analysis_obj = AnalysisResult(**doc["analysis"])
    timeline_raw = doc.get("timeline") or []
    timeline_objs = [TimelineEvent(**t) for t in timeline_raw]

    postmortem = PostmortemGenerator.generate(
        incident=doc,
        analysis=analysis_obj,
        timeline=timeline_objs
    )

    # Persist in postmortems collection
    pm_col = get_db_collection("postmortems")
    # Check if one already exists for this incident
    existing = await pm_col.find_one({"incident_ref_id": postmortem.incident_ref_id})
    if existing:
        # Update existing
        pm_dict = postmortem.model_dump()
        pm_dict["_id"] = existing["_id"]
        await pm_col.update_one({"_id": existing["_id"]}, {"$set": pm_dict})
    else:
        pm_dict = postmortem.model_dump()
        pm_dict["_id"] = postmortem.id
        await pm_col.insert_one(pm_dict)

    return postmortem

@router.get("/", response_model=List[PostmortemReport])
async def list_postmortems():
    pm_col = get_db_collection("postmortems")
    cursor = pm_col.find({}, sort=[("created_at", -1)])
    items = await cursor.to_list(length=100)
    return [PostmortemReport(**item) for item in items]

@router.get("/{pm_id}", response_model=PostmortemReport)
async def get_postmortem(pm_id: str):
    pm_col = get_db_collection("postmortems")
    item = await pm_col.find_one({"$or": [{"id": pm_id}, {"incident_ref_id": pm_id}]})
    if not item:
        raise HTTPException(status_code=404, detail="Postmortem report not found.")
    return PostmortemReport(**item)

@router.patch("/{pm_id}", response_model=PostmortemReport)
async def update_postmortem(pm_id: str, patch: PostmortemUpdate):
    """Allow engineer to edit postmortem details or change status (Draft/Published)."""
    pm_col = get_db_collection("postmortems")
    item = await pm_col.find_one({"$or": [{"id": pm_id}, {"incident_ref_id": pm_id}]})
    if not item:
        raise HTTPException(status_code=404, detail="Postmortem report not found.")

    update_fields = {"updated_at": datetime.now(timezone.utc)}
    for field, val in patch.model_dump(exclude_unset=True).items():
        if val is not None:
            update_fields[field] = val

    await pm_col.update_one({"_id": item["_id"]}, {"$set": update_fields})
    updated = await pm_col.find_one({"_id": item["_id"]})
    return PostmortemReport(**updated)

@router.get("/{pm_id}/export")
async def export_postmortem_markdown(pm_id: str):
    """Export the postmortem report as clean Markdown text."""
    pm_col = get_db_collection("postmortems")
    item = await pm_col.find_one({"$or": [{"id": pm_id}, {"incident_ref_id": pm_id}]})
    if not item:
        raise HTTPException(status_code=404, detail="Postmortem report not found.")

    pm_obj = PostmortemReport(**item)
    markdown_content = PostmortemGenerator.export_as_markdown(pm_obj)

    return Response(
        content=markdown_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename={pm_obj.incident_ref_id}_postmortem.md"}
    )
