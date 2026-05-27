from pydantic import BaseModel
from typing import List


class OrderItemRequest(BaseModel):
    """
    Single cart item
    """
    product_id: str
    qty: int


class OrderCreateRequest(BaseModel):
    """
    Order creation payload
    """
    items: List[OrderItemRequest]
    payment_mode: str