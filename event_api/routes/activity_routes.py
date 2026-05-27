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

    Used for:
    - PRODUCT_SEARCHED
    - CART_ITEM_ADDED
    - CART_QTY_INCREASED
    - CART_QTY_DECREASED
    - CART_ITEM_REMOVED
    - CHECKOUT_STARTED
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

    enriched_payload = {
        "user_id": user_data["user_id"],
        **payload.payload
    }

    event = build_event(
        payload.event_type,
        enriched_payload
    )

    publish_event(
        "user_activity_events",
        event
    )

    return {
        "message": "Activity tracked"
    }