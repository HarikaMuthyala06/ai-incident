from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import List, Optional, Dict, Any
from app.models.document import KnowledgeDocCreate, KnowledgeDocResponse
from app.core.database import get_db_collection
from app.services.rag_pipeline import ManualRAGPipeline
from app.services.seed_knowledge import seed_default_knowledge_base

router = APIRouter()

@router.get("/", response_model=List[KnowledgeDocResponse])
async def list_knowledge_documents():
    """List all ingested technical guides and troubleshooting runbooks."""
    # Ensure default runbooks are seeded
    await seed_default_knowledge_base()

    docs_col = get_db_collection("knowledge_documents")
    cursor = docs_col.find({}, sort=[("created_at", -1)])
    docs = await cursor.to_list(length=100)

    results = []
    for d in docs:
        results.append(KnowledgeDocResponse(
            id=d.get("id", str(d.get("_id"))),
            title=d.get("title", "Untitled Document"),
            category=d.get("category", "General"),
            source_filename=d.get("source_filename", "manual.txt"),
            content_preview=d.get("content_preview", ""),
            total_chunks=d.get("total_chunks", 1),
            created_at=d.get("created_at")
        ))
    return results

@router.get("/{doc_id}/chunks")
async def get_document_chunks(doc_id: str):
    """
    EDUCATIONAL INSPECTION ENDPOINT:
    Returns raw chunk segments, word tokens, chunk boundary indices, and sample embedding vectors.
    Allows students to see how documents get broken down and represented numerically.
    """
    chunks_col = get_db_collection("knowledge_chunks")
    cursor = chunks_col.find({"doc_id": doc_id}, sort=[("chunk_index", 1)])
    chunks = await cursor.to_list(length=100)
    
    # Return chunks with first 8 embedding dimensions previewed
    inspected = []
    for c in chunks:
        emb = c.get("embedding", [])
        inspected.append({
            "chunk_id": c.get("chunk_id"),
            "chunk_index": c.get("chunk_index"),
            "category": c.get("category"),
            "text": c.get("text"),
            "text_length": len(c.get("text", "")),
            "embedding_dimensions": len(emb),
            "embedding_sample": emb[:6] if emb else []  # First 6 float dimensions
        })
    return {
        "doc_id": doc_id,
        "total_chunks": len(inspected),
        "chunks": inspected
    }

@router.post("/upload", response_model=KnowledgeDocResponse)
async def upload_document(
    title: str = Form(...),
    category: str = Form("General Troubleshooting"),
    file: Optional[UploadFile] = File(None),
    content_text: Optional[str] = Form(None)
):
    """
    Upload and index technical document into vector knowledge base.
    Supports PDF (via PyMuPDF), DOCX (via python-docx), TXT, LOG, Markdown, or manual text paste.
    """
    if not file and not content_text:
        raise HTTPException(status_code=400, detail="Provide either an uploaded file or content_text.")

    source_filename = "manual_entry.txt"
    raw_content = ""

    if file:
        source_filename = file.filename
        file_bytes = await file.read()
        raw_content = ManualRAGPipeline.extract_text_from_file(file_bytes, file.filename)
    elif content_text:
        raw_content = content_text

    if not raw_content or len(raw_content.strip()) < 10:
        raise HTTPException(status_code=400, detail="The extracted document content is empty or too short.")

    doc_record = await ManualRAGPipeline.index_document(
        title=title,
        category=category,
        content=raw_content,
        source_filename=source_filename
    )

    return KnowledgeDocResponse(
        id=doc_record["id"],
        title=doc_record["title"],
        category=doc_record["category"],
        source_filename=doc_record["source_filename"],
        content_preview=doc_record["content_preview"],
        total_chunks=doc_record["total_chunks"],
        created_at=doc_record["created_at"]
    )

@router.post("/seed")
async def trigger_seed():
    """Manual trigger to re-seed default SRE runbooks."""
    await seed_default_knowledge_base()
    return {"message": "Knowledge base seeded with default troubleshooting guides."}
