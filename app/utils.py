from typing import Any, Dict
from bson import ObjectId
from datetime import datetime, date


def serialize_mongo_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Mongo document to JSON-serializable dict:
    - Replace _id with id (str)
    - Convert datetime to ISO date string (YYYY-MM-DD)
    """
    if not doc:
        return doc
    out = doc.copy()
    _id = out.pop("_id", None)
    if _id is not None:
        out["id"] = str(_id)
    # convert joining_date if present
    jd = out.get("joining_date")
    if isinstance(jd, (datetime,)):
        # store as date-string to match pydantic model's date type
        out["joining_date"] = jd.date().isoformat()
    elif isinstance(jd, date):
        out["joining_date"] = jd.isoformat()
    return out
