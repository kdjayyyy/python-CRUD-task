import logging
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError
from app.config import settings
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class MongoClientWrapper:
    def __init__(self, uri: str, db_name: str):
        self._uri = uri
        self._db_name = db_name
        self._client: Optional[AsyncIOMotorClient] = None

    async def connect(self) -> None:
        if self._client:
            return
        # create client
        self._client = AsyncIOMotorClient(str(self._uri), serverSelectionTimeoutMS=5000)

        try:
            # ping to ensure connection
            await self._client.admin.command("ping")
            logger.info("Connected to MongoDB")
        except ServerSelectionTimeoutError as e:
            logger.exception("Failed to connect to MongoDB: %s", e)
            raise

    def get_database(self):
        if not self._client:
            raise RuntimeError("Mongo client not connected. Call connect() in startup.")
        return self._client[self._db_name]

    async def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
            logger.info("MongoDB connection closed")


mongo_client = MongoClientWrapper(settings.MONGO_URI, settings.MONGO_DB_NAME)


async def ensure_indexes_and_collections(db) -> None:
    """
    Idempotently ensure the employees collection exists and has unique index on employee_id.
    Optionally create collection with JSON Schema validator (controlled by env).
    """
    coll_name = "employees"
    # Optionally create collection with validator (if enabled)
    if settings.CREATE_COLLECTION_VALIDATOR:
        # JSON Schema validator to ensure required fields and types.
        validator = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["employee_id", "name", "department", "salary", "joining_date", "skills"],
                "properties": {
                    "employee_id": {"bsonType": "string"},
                    "name": {"bsonType": "string"},
                    "department": {"bsonType": "string"},
                    "salary": {"bsonType": "number"},
                    "joining_date": {"bsonType": "date"},
                    "skills": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"}
                    }
                }
            }
        }
        existing = await db.list_collection_names()
        if coll_name not in existing:
            await db.create_collection(coll_name, validator=validator)
            logger.info("Created collection %s with validator", coll_name)
        else:
            # try to apply validator via collMod (idempotent-ish)
            try:
                await db.command({
                    "collMod": coll_name,
                    "validator": validator,
                    "validationLevel": "moderate"
                })
                logger.info("Collection validator updated for %s", coll_name)
            except Exception:
                logger.debug("Could not modify validator (may not be supported)")

    coll = db[coll_name]
    # ensure unique index on employee_id
    await coll.create_index("employee_id", unique=True)
    # ensure an index on joining_date for sort queries (helpful)
    await coll.create_index([("joining_date", -1)])
    logger.info("Indexes ensured for collection %s", coll_name)


# helper to convert date (pydantic date) to datetime stored in Mongo
def to_mongo_datetime(date_obj):
    """
    Convert date or datetime to timezone-aware UTC datetime for storing in MongoDB.
    Accepts datetime.date or datetime.datetime.
    """
    if date_obj is None:
        return None
    if isinstance(date_obj, datetime):
        dt = date_obj
    else:
        # assume date-like (datetime.date)
        dt = datetime(date_obj.year, date_obj.month, date_obj.day)
    # set timezone UTC to avoid ambiguous comparisons
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt
