from pydantic import BaseModel
from typing import Dict, Any


class ActivityTrackRequest(BaseModel):
    """
    Generic customer activity event
    """
    event_type: str
    payload: Dict[str, Any]