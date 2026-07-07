from fastapi import APIRouter, HTTPException, Header

from event_api.schemas.activity_schema import ActivityTrackRequest
from event_api.security import decode_access_token

from kafka_engine.producers.producer import publish_event

from uuid import uuid4
from datetime import datetime, UTC

router = APIRouter(
    prefix="/activity",
    tags=["Activity Tracking"]
)

# -------------------------------------------------------------------
# DYNAMIC TOPIC ROUTING MAP
# Maps frontend event types to their specific backend Kafka topics
# -------------------------------------------------------------------
EVENT_TOPIC_MAP = {
    # Browsing Events
    "PRODUCT_SEARCHED": "user_browsing_events",
    "PRODUCT_VIEWED": "user_browsing_events",
    "OUT_OF_STOCK_INTEREST": "user_browsing_events",
    
    # Cart Events
    "CART_ITEM_ADDED": "user_cart_events",
    "CART_QTY_INCREASED": "user_cart_events",
    "CART_QTY_DECREASED": "user_cart_events",
    "CART_ITEM_REMOVED": "user_cart_events",
    "CHECKOUT_STARTED": "user_cart_events"
}


def build_event(event_type, payload):
    """
    Standard activity event structure
    """
    return {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "event_version": "1.0",
        "event_ts": datetime.now(UTC).isoformat(),
        "source_system": "customer-ui",
        "payload": payload
    }


@router.post("/track")
def track_activity(
    payload: ActivityTrackRequest,
    authorization: str = Header(None)
):
    """
    Generic customer activity tracking API
    """

    # Validate JWT presence
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization token missing"
        )

    try:
        token = authorization.split(" ")[1]
    except:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format"
        )

    # Decode user token
    user_data = decode_access_token(token)

    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
        
    # ---------------------------------------------------------------
    # 1. Determine Target Topic
    # ---------------------------------------------------------------
    target_topic = EVENT_TOPIC_MAP.get(payload.event_type)
    
    # Fail fast if the frontend sends an unmapped or misspelled event type
    if not target_topic:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported event type: {payload.event_type}"
        )

    # 2. Enrich Payload
    enriched_payload = {
        "user_id": user_data["user_id"],
        **payload.payload
    }

    # 3. Build Event Envelope
    event = build_event(
        payload.event_type,
        enriched_payload
    )

    # ---------------------------------------------------------------
    # 4. Publish to the dynamically resolved topic
    # ---------------------------------------------------------------
    publish_event(
        target_topic,
        event
    )

    return {
        "message": f"Activity tracked to {target_topic}"
    }