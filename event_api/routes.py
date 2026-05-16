from fastapi import APIRouter
from event_api.schemas import EventSchema
from kafka_engine.producers.producer import publish_event
from event_api.product_store import products

router = APIRouter()


@router.get("/products")
def get_products():
    # Simulates a database fetch to get all current products
    return products

@router.post("/product-event")
def product_event(event: EventSchema):
    # 1. Send the raw event to Kafka
    publish_event("product_events", event.model_dump())

    # 2. Update our local "database" simulation based on the event type
    if event.event_type == "PRODUCT_CREATED":
        # Add new product to the list
        products.append(event.payload)

    elif event.event_type == "PRICE_UPDATED":
        # Find the specific product and update its price
        for product in products:
            if product["product_id"] == event.payload["product_id"]:
                product["price"] = event.payload["new_price"]

    elif event.event_type == "PRODUCT_DELISTED":
        # Rebuild the list, keeping everything EXCEPT the delisted product
        products[:] = [
            p for p in products
            if p["product_id"] != event.payload["product_id"]
        ]

    return {
        "status": "accepted",
        "event_type": event.event_type,
        "published_to": "product_events"
    }


@router.post("/inventory-event")
def inventory_event(event: EventSchema):
    publish_event("inventory_events", event.model_dump())

    # Find the specific product and update its available stock
    for product in products:
        if product["product_id"] == event.payload["product_id"]:
            product["stock_qty"] = event.payload["stock_qty"]

    return {
        "status": "accepted",
        "event_type": event.event_type,
        "published_to": "inventory_events"
    }


# --- Below endpoints only publish to Kafka (no local state updates yet) ---

@router.post("/cart-event")
def cart_event(event: EventSchema):
    publish_event("cart_events", event.model_dump())

    return {
        "status": "accepted",
        "event_type": event.event_type,
        "published_to": "cart_events"
    }


@router.post("/activity-event")
def activity_event(event: EventSchema):
    publish_event("user_activity_events", event.model_dump())

    return {
        "status": "accepted",
        "event_type": event.event_type,
        "published_to": "user_activity_events"
    }


@router.post("/order-event")
def order_event(event: EventSchema):
    publish_event("order_events", event.model_dump())

    return {
        "status": "accepted",
        "event_type": event.event_type,
        "published_to": "order_events"
    }