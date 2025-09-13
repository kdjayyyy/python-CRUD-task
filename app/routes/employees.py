from fastapi import APIRouter, HTTPException, status, Depends
from pymongo import ReturnDocument
from typing import List
from app.schemas import EmployeeCreate, EmployeeOut, EmployeeUpdate
from app.db import mongo_client, to_mongo_datetime
from app.utils import serialize_mongo_doc
from pymongo.errors import DuplicateKeyError
from app.db import MongoClientWrapper  # for typing only
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def get_db():
    """ Dependency to fetch DB instance (assumes startup connected). """
    db = mongo_client.get_database()
    return db


@router.post("", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
async def create_employee(payload: EmployeeCreate):
    db = get_db()
    coll = db["employees"]
    # prepare document
    doc = payload.dict()
    # convert joining_date -> datetime (UTC) for storage
    doc["joining_date"] = to_mongo_datetime(doc["joining_date"])
    try:
        res = await coll.insert_one(doc)
    except DuplicateKeyError:
        # employee_id unique index violated
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="employee_id already exists")
    except Exception as exc:
        logger.exception("Failed to insert employee: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to create employee")
    created = await coll.find_one({"_id": res.inserted_id})
    return serialize_mongo_doc(created)


@router.get("/{employee_id}", response_model=EmployeeOut)
async def get_employee(employee_id: str):
    db = get_db()
    coll = db["employees"]
    doc = await coll.find_one({"employee_id": employee_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="employee not found")
    return serialize_mongo_doc(doc)


# Simple list-by-department with sorting (helpful during setup testing)
@router.get("", response_model=List[EmployeeOut])
async def list_employees(department: str = None, limit: int = 100):
    db = get_db()
    coll = db["employees"]
    query = {}
    if department:
        query["department"] = department
    cursor = coll.find(query).sort("joining_date", -1).limit(limit)
    documents = []
    async for doc in cursor:
        documents.append(serialize_mongo_doc(doc))
    return documents


@router.put("/{employee_id}", response_model=EmployeeOut)
async def update_employee(employee_id: str, payload: EmployeeUpdate):
    """
    Partial update: only provided fields are applied.
    Returns 400 if no fields provided, 404 if employee not found.
    """
    db = get_db()
    coll = db["employees"]

    # pydantic v2: use model_dump to get dict, excluding None values
    update_fields = payload.model_dump(exclude_none=True)
    if not update_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="no fields to update")

    # convert joining_date to Mongo datetime if present
    if "joining_date" in update_fields:
        update_fields["joining_date"] = to_mongo_datetime(update_fields["joining_date"])

    try:
        updated_doc = await coll.find_one_and_update(
            {"employee_id": employee_id},
            {"$set": update_fields},
            return_document=ReturnDocument.AFTER
        )
    except Exception as exc:
        logger.exception("Update failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to update employee")

    if not updated_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="employee not found")

    return serialize_mongo_doc(updated_doc)


@router.delete("/{employee_id}", status_code=status.HTTP_200_OK)
async def delete_employee(employee_id: str):
    db = get_db()
    coll = db["employees"]
    res = await coll.delete_one({"employee_id": employee_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="employee not found")
    return {"detail": "employee deleted"}
