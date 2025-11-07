from typing import Any, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel
import os

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "appdb")

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None

async def get_db() -> AsyncIOMotorDatabase:
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(DATABASE_URL)
        _db = _client[DATABASE_NAME]
    return _db

async def create_document(collection: str, data: Dict[str, Any]) -> Dict[str, Any]:
    db = await get_db()
    payload = {**data, "_created_at": __import__("datetime").datetime.utcnow()}
    result = await db[collection].insert_one(payload)
    payload["_id"] = str(result.inserted_id)
    return payload

async def get_documents(collection: str, filter_dict: Optional[Dict[str, Any]] = None, limit: int = 50):
    db = await get_db()
    cursor = db[collection].find(filter_dict or {}).sort("_created_at", -1).limit(limit)
    docs = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])  # stringify ObjectId
        docs.append(doc)
    return docs
