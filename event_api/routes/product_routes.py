# This is API layer.
# Admin actions: DB write , Kafka event publish
# Customer actions: DB read

from fastapi import APIRouter, HTTPException
from event_api.schemas.product_schema import (
    ProductCreate,
    ProductPriceUpdate,
    ProductInventoryUpdate
)
from event_api.services.product_service import (
    create_product,
    get_active_products,
    update_product_price,
    update_inventory,
    deactivate_product
)
from kafka_engine.producers.producer import publish_event
from uuid import uuid4
from datetime import datetime, UTC


router = APIRouter()


def build_event(event_type, source_system, payload):
    """
    Standard Kafka event builder
    """

    return {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "event_version": "1.0",
        "event_ts": datetime.now(UTC).isoformat(),
        "source_system": source_system,
        "payload": payload
    }


@router.post("/products")
def create_new_product(product: ProductCreate):
    """
    Admin creates product
    """

    create_product(product)

    event = build_event(
        "PRODUCT_CREATED",
        "admin-ui",
        product.model_dump()
    )

    publish_event("product_events", event)

    return {"message": "Product created successfully"}


@router.get("/products")
def fetch_products():
    """
    Customer fetches active catalog
    """

    products = get_active_products()

    return [
        {
            "product_id": p.product_id,
            "product_name": p.product_name,
            "category": p.category,
            "price": p.price,
            "stock_qty": p.stock_qty
        }
        for p in products
    ]


@router.put("/products/{product_id}/price")
def update_price(product_id: str, payload: ProductPriceUpdate):
    """
    Admin updates pricing
    """

    product = update_product_price(product_id, payload.price)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    event = build_event(
        "PRICE_UPDATED",
        "admin-ui",
        {
            "product_id": product_id,
            "price": payload.price
        }
    )

    publish_event("product_events", event)

    return {"message": "Price updated"}


@router.put("/products/{product_id}/inventory")
def update_stock(product_id: str, payload: ProductInventoryUpdate):
    """
    Admin updates stock
    """

    product = update_inventory(product_id, payload.stock_qty)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    event = build_event(
        "INVENTORY_UPDATED",
        "admin-ui",
        {
            "product_id": product_id,
            "stock_qty": payload.stock_qty
        }
    )

    publish_event("inventory_events", event)

    return {"message": "Inventory updated"}


@router.delete("/products/{product_id}")
def delist_product(product_id: str):
    """
    Admin soft deletes product
    """

    product = deactivate_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    event = build_event(
        "PRODUCT_DELISTED",
        "admin-ui",
        {
            "product_id": product_id
        }
    )

    publish_event("product_events", event)

    return {"message": "Product delisted"}