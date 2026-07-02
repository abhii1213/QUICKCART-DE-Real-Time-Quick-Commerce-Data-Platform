from fastapi import APIRouter, HTTPException, Header

from event_api.schemas.order_schema import OrderCreateRequest
from event_api.services.order_service import create_order
from event_api.security import decode_access_token

from kafka_engine.producers.producer import publish_event

from uuid import uuid4
from datetime import datetime, UTC

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


def build_event(event_type, payload):
    """
    Build standard Kafka business event
    """
    return {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "event_version": "1.0",
        "event_ts": datetime.now(UTC).isoformat(),
        "source_system": "customer-ui",
        "payload": payload
    }


@router.post("")
def place_order(
    payload: OrderCreateRequest,
    authorization: str = Header(None)
):
    """
    Create customer order

    Flow:
    1. Validate JWT
    2. Extract user_id
    3. Create DB transaction
    4. Publish ORDER_PLACED event
    """

    # Check JWT token presence
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization token missing"
        )

    try:
        # Extract raw token from:
        # Bearer xxxxx
        token = authorization.split(" ")[1]
    except:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format"
        )

    # Decode JWT
    user_payload = decode_access_token(token)

    if not user_payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user_id = user_payload["user_id"]

    # Create transactional order
    result, error = create_order(user_id, payload)

    if error:
        raise HTTPException(
            status_code=400,
            detail=error
        )

    # Publish analytics event
    event = build_event(
        "ORDER_PLACED",
        {
            "order_id": result["order_id"],
            "user_id": user_id,
            "total_amount": result["total_amount"],
            "payment_mode": payload.payment_mode,
            "items": [
                {
                    "product_id": item["product_id"],
                    "qty": item["qty"],
                    "unit_price": item["unit_price"]
                }
                for item in result["items"]
            ]
        }
    )

    publish_event("user_activity_events", event)

    # for inventory in result["updated_inventory"]:
    #     inventory_event = build_event(
    #         "INVENTORY_UPDATED",
    #         {
    #             "product_id": inventory["product_id"],
    #             "stock_qty": inventory["stock_qty"]
    #         }
    #     )
    #     publish_event(
    #         "inventory_events",
    #         inventory_event
    #     )

    return {
        "message": "Order placed successfully",
        "order_id": result["order_id"],
        "total_amount": result["total_amount"]
    }