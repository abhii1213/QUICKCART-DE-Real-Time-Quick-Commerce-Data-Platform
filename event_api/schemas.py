from pydantic import BaseModel
from typing import Dict, Any


class EventSchema(BaseModel):
    event_id: str
    event_type: str
    event_version: str
    event_ts: str
    source_system: str
    payload: Dict[str, Any]