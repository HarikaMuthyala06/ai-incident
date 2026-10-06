import logging
import math
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

logger = logging.getLogger("incident_agent.db")

class InMemoryCollection:
    """
    Educational Fallback Collection:
    Mirrors standard MongoDB Async Driver methods (find, insert_one, update_one, delete_one, aggregate)
    in Python memory. This allows students to develop and test immediately even before setting up
    MongoDB Atlas, while learning the exact MongoDB query patterns.
    """
    def __init__(self, name: str):
        self.name = name
        self.documents: List[Dict[str, Any]] = []

    async def insert_one(self, doc: Dict[str, Any]):
        # Ensure copy to avoid external mutation
        item = dict(doc)
        if "_id" not in item:
            import uuid
            item["_id"] = str(uuid.uuid4())
        self.documents.append(item)
        class Result:
            inserted_id = item["_id"]
        return Result()

    def _doc_matches(self, doc: Dict[str, Any], filter_query: Dict[str, Any]) -> bool:
        if not filter_query:
            return True
        for k, v in filter_query.items():
            if k == "$or":
                if not any(self._doc_matches(doc, cond) for cond in v):
                    return False
            elif k == "$and":
                if not all(self._doc_matches(doc, cond) for cond in v):
                    return False
            else:
                if doc.get(k) != v:
                    return False
        return True

    async def find_one(self, filter_query: Dict[str, Any]):
        for doc in self.documents:
            if self._doc_matches(doc, filter_query):
                return dict(doc)
        return None

    def find(self, filter_query: Optional[Dict[str, Any]] = None, sort: Optional[List] = None):
        filter_query = filter_query or {}
        matched = []
        for doc in self.documents:
            if self._doc_matches(doc, filter_query):
                matched.append(dict(doc))
        
        # Sort if requested (e.g. [("created_at", -1)])
        if sort:
            field, direction = sort[0]
            reverse = direction == -1
            matched.sort(key=lambda x: str(x.get(field, "")), reverse=reverse)

        class Cursor:
            def __init__(self, items):
                self.items = items
            async def to_list(self, length: Optional[int] = None):
                if length is not None:
                    return self.items[:length]
                return self.items
            def __aiter__(self):
                self._iter = iter(self.items)
                return self
            async def __anext__(self):
                try:
                    return next(self._iter)
                except StopIteration:
                    raise StopAsyncIteration
        return Cursor(matched)

    async def update_one(self, filter_query: Dict[str, Any], update_doc: Dict[str, Any]):
        for idx, doc in enumerate(self.documents):
            if self._doc_matches(doc, filter_query):
                if "$set" in update_doc:
                    doc.update(update_doc["$set"])
                class Result:
                    modified_count = 1
                return Result()
        class Result:
            modified_count = 0
        return Result()

    async def delete_one(self, filter_query: Dict[str, Any]):
        for idx, doc in enumerate(self.documents):
            if self._doc_matches(doc, filter_query):
                del self.documents[idx]
                class Result:
                    deleted_count = 1
                return Result()
        class Result:
            deleted_count = 0
        return Result()

    async def count_documents(self, filter_query: Optional[Dict[str, Any]] = None):
        filter_query = filter_query or {}
        count = 0
        for doc in self.documents:
            if self._doc_matches(doc, filter_query):
                count += 1
        return count


class DatabaseManager:
    client: Optional[AsyncIOMotorClient] = None
    db = None
    is_connected_to_mongo: bool = False
    in_memory_db: Dict[str, InMemoryCollection] = {}

    def get_collection(self, collection_name: str):
        if self.is_connected_to_mongo and self.db is not None:
            return self.db[collection_name]
        if collection_name not in self.in_memory_db:
            self.in_memory_db[collection_name] = InMemoryCollection(collection_name)
        return self.in_memory_db[collection_name]

    async def connect(self):
        try:
            logger.info(f"Connecting to MongoDB at: {settings.MONGODB_URI}...")
            # Short timeout to avoid blocking server boot if local mongo is down
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=2000
            )
            # Ping to verify connection
            await self.client.admin.command('ping')
            self.db = self.client[settings.DATABASE_NAME]
            self.is_connected_to_mongo = True
            logger.info("Successfully connected to MongoDB Database!")
        except Exception as e:
            self.is_connected_to_mongo = False
            logger.warning(
                f"[DATABASE NOTICE] Could not connect to MongoDB ({e}). "
                "Running in educational In-Memory mode. All CRUD operations & RAG vector search "
                "will work smoothly in Python memory for learning!"
            )

    async def disconnect(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")

db_manager = DatabaseManager()

def get_db_collection(collection_name: str):
    """Dependency helper to retrieve target collection."""
    return db_manager.get_collection(collection_name)

def calculate_cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Mathematical Implementation of Cosine Similarity:
    sim(A, B) = (A . B) / (||A|| * ||B||)
    Returns a score between -1.0 and 1.0 (typically 0.0 to 1.0 for normalized text embeddings).
    """
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)
