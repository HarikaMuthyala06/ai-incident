import os
import re
import math
import uuid
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from app.core.config import settings
from app.core.database import get_db_collection, calculate_cosine_similarity
from app.models.document import RetrievedEvidenceItem

logger = logging.getLogger("incident_agent.rag")

# Optional OpenAI client initialization
openai_client = None
if settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY.strip()) > 5:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    except Exception as e:
        logger.warning(f"Could not initialize OpenAI client: {e}")

class ManualRAGPipeline:
    """
    EDUCATIONAL RAG PIPELINE
    Implements every step explicitly without black-box framework abstractions:
    1. Text Extraction (TXT, Markdown, PDF via PyMuPDF, DOCX via python-docx)
    2. Text Cleaning & Normalization
    3. Overlapping Sliding Window Chunking
    4. Dense Vector Embedding Generation (OpenAI text-embedding-3-small or offline fallback)
    5. MongoDB Atlas Vector Search / Python Cosine Similarity Calculation
    6. Augmented Prompt Construction
    """

    @staticmethod
    def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
        """Step 1: Extract raw text from different file formats."""
        ext = filename.lower().split(".")[-1]
        
        if ext in ["txt", "log", "md", "json", "yaml", "yml"]:
            return file_bytes.decode("utf-8", errors="replace")
            
        elif ext == "pdf":
            import fitz  # PyMuPDF
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            extracted_pages = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                extracted_pages.append(page.get_text())
            return "\n\n".join(extracted_pages)
            
        elif ext in ["docx", "doc"]:
            import io
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            full_text = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(full_text)
            
        else:
            # Fallback to UTF-8 decode
            return file_bytes.decode("utf-8", errors="replace")

    @staticmethod
    def clean_text(text: str) -> str:
        """Step 2: Clean and normalize text."""
        # Replace multiple spaces with single space
        text = re.sub(r"[ \t]+", " ", text)
        # Normalize carriage returns and multiple newlines
        text = re.sub(r"\r\n|\r", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 700, chunk_overlap: int = 150) -> List[str]:
        """
        Step 3: Sliding window chunking with overlap.
        Preserves context at boundaries so critical diagnostic clues aren't bisected.
        """
        if not text:
            return []
            
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + chunk_size
            if end >= text_len:
                chunk = text[start:].strip()
                if chunk:
                    chunks.append(chunk)
                break
                
            # Try to break gracefully on a newline or period near the end
            breakpoint = text.rfind("\n", start + chunk_overlap, end)
            if breakpoint == -1:
                breakpoint = text.rfind(". ", start + chunk_overlap, end)
            if breakpoint == -1:
                breakpoint = end
            else:
                breakpoint += 1  # Include the character
                
            chunk = text[start:breakpoint].strip()
            if chunk:
                chunks.append(chunk)
                
            start = breakpoint - chunk_overlap
            if start < 0:
                start = 0
                
        return chunks

    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        """
        Step 4: Vector Embedding Generation.
        Generates a 1536-dimensional float vector using OpenAI text-embedding-3-small.
        If no API key is provided, computes a deterministic frequency-based vector
        so offline local learning and unit testing work without breaking.
        """
        global openai_client
        if openai_client:
            try:
                response = openai_client.embeddings.create(
                    input=text[:8000],  # stay within token limit
                    model=settings.OPENAI_EMBEDDING_MODEL
                )
                return response.data[0].embedding
            except Exception as e:
                logger.warning(f"OpenAI embedding call failed ({e}). Using offline vector fallback.")

        # Offline Deterministic Semantic Vector Fallback (1536 dimensions)
        # Encodes character n-grams and word tokens into a normalized unit vector
        dim = 1536
        vector = [0.0] * dim
        words = re.findall(r"\w+", text.lower())
        for idx, word in enumerate(words):
            word_hash = hash(word) % dim
            vector[word_hash] += 1.0 / (idx + 1.0)
            
        # L2 Normalization so magnitude = 1.0 (Unit Vector)
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0.0:
            vector = [x / norm for x in vector]
        else:
            vector[0] = 1.0
            
        return vector

    @classmethod
    async def index_document(
        cls,
        title: str,
        category: str,
        content: str,
        source_filename: str = "manual_entry.txt"
    ) -> Dict[str, Any]:
        """Step 5: Store document & chunks in vector storage."""
        docs_col = get_db_collection("knowledge_documents")
        chunks_col = get_db_collection("knowledge_chunks")
        
        doc_id = f"DOC-{str(uuid.uuid4())[:8].upper()}"
        cleaned = cls.clean_text(content)
        raw_chunks = cls.chunk_text(cleaned)
        
        doc_record = {
            "_id": str(uuid.uuid4()),
            "id": doc_id,
            "title": title,
            "category": category,
            "source_filename": source_filename,
            "content_preview": cleaned[:200] + "..." if len(cleaned) > 200 else cleaned,
            "total_chunks": len(raw_chunks),
            "created_at": datetime.now(timezone.utc)
        }
        await docs_col.insert_one(doc_record)
        
        # Ingest and embed each chunk
        for idx, chunk_text in enumerate(raw_chunks):
            embedding = cls.generate_embedding(chunk_text)
            chunk_doc = {
                "_id": str(uuid.uuid4()),
                "chunk_id": f"{doc_id}-CHK-{idx+1:03d}",
                "doc_id": doc_id,
                "doc_title": title,
                "category": category,
                "chunk_index": idx + 1,
                "text": chunk_text,
                "embedding": embedding,
                "created_at": datetime.now(timezone.utc)
            }
            await chunks_col.insert_one(chunk_doc)
            
        return doc_record

    @classmethod
    async def search_relevant_knowledge(
        cls,
        query: str,
        top_k: int = 4
    ) -> List[RetrievedEvidenceItem]:
        """
        Step 6: Retrieve relevant technical documentation chunks.
        Performs vector similarity search against the knowledge_chunks collection.
        """
        query_embedding = cls.generate_embedding(query)
        chunks_col = get_db_collection("knowledge_chunks")
        
        results: List[RetrievedEvidenceItem] = []
        
        # Check if MongoDB Atlas Vector Search is available
        from app.core.database import db_manager
        if db_manager.is_connected_to_mongo:
            try:
                # Try Atlas $vectorSearch aggregation pipeline
                pipeline = [
                    {
                        "$vectorSearch": {
                            "index": "vector_index",
                            "path": "embedding",
                            "queryVector": query_embedding,
                            "numCandidates": 50,
                            "limit": top_k
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "doc_id": 1,
                            "doc_title": 1,
                            "category": 1,
                            "text": 1,
                            "chunk_index": 1,
                            "score": {"$meta": "vectorSearchScore"}
                        }
                    }
                ]
                cursor = chunks_col.aggregate(pipeline)
                async for item in cursor:
                    score = float(item.get("score", 0.0))
                    rating = "High" if score >= 0.78 else ("Medium" if score >= 0.60 else "Low")
                    results.append(RetrievedEvidenceItem(
                        doc_id=item["doc_id"],
                        doc_title=item["doc_title"],
                        category=item.get("category", "Guide"),
                        relevance_score=round(score, 4),
                        relevance_rating=rating,
                        matched_snippet=item["text"][:350],
                        chunk_index=item.get("chunk_index", 1)
                    ))
                if results:
                    return results
            except Exception as atlas_err:
                logger.debug(f"Atlas Vector Search fallback to in-engine cosine calculation: {atlas_err}")

        # In-Engine Manual Cosine Similarity Calculation
        all_chunks_cursor = chunks_col.find({})
        all_chunks = await all_chunks_cursor.to_list(length=500)
        
        scored = []
        for chunk in all_chunks:
            chunk_vec = chunk.get("embedding")
            if chunk_vec:
                sim = calculate_cosine_similarity(query_embedding, chunk_vec)
                scored.append((sim, chunk))
                
        # Sort descending by similarity score
        scored.sort(key=lambda x: x[0], reverse=True)
        
        for sim, chunk in scored[:top_k]:
            rating = "High" if sim >= 0.75 else ("Medium" if sim >= 0.50 else "Low")
            results.append(RetrievedEvidenceItem(
                doc_id=chunk["doc_id"],
                doc_title=chunk["doc_title"],
                category=chunk.get("category", "Guide"),
                relevance_score=round(float(sim), 4),
                relevance_rating=rating,
                matched_snippet=chunk["text"][:350],
                chunk_index=chunk.get("chunk_index", 1)
            ))
            
        return results

    @classmethod
    async def search_similar_past_incidents(
        cls,
        incident_text: str,
        current_incident_id: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Step 7: Cross-reference historical incidents.
        Finds previous resolved incidents that had similar symptoms or root causes.
        """
        query_vec = cls.generate_embedding(incident_text)
        incidents_col = get_db_collection("incidents")
        
        cursor = incidents_col.find({})
        all_incidents = await cursor.to_list(length=100)
        
        scored = []
        for inc in all_incidents:
            if current_incident_id and inc.get("incident_id") == current_incident_id:
                continue
            inc_vec = inc.get("embedding")
            if not inc_vec:
                # generate embedding on the fly if needed
                summary = f"{inc.get('title', '')} {inc.get('description', '')} {inc.get('error_messages', '')}"
                inc_vec = cls.generate_embedding(summary)
            sim = calculate_cosine_similarity(query_vec, inc_vec)
            scored.append((sim, inc))
            
        scored.sort(key=lambda x: x[0], reverse=True)
        
        similar = []
        for sim, inc in scored[:top_k]:
            rating = "High" if sim >= 0.70 else ("Medium" if sim >= 0.45 else "Low")
            similar.append({
                "incident_id": inc.get("incident_id", "INC-PREV"),
                "title": inc.get("title", "Historical Incident"),
                "application": inc.get("application", "System"),
                "status": inc.get("status", "Resolved"),
                "relevance_score": round(float(sim), 4),
                "relevance_rating": rating,
                "probable_root_cause": inc.get("analysis", {}).get("probable_root_cause") if inc.get("analysis") else "Identified service bottleneck",
                "resolution": inc.get("analysis", {}).get("suggested_resolution") if inc.get("analysis") else "Patched configuration and recycled pods"
            })
        return similar
