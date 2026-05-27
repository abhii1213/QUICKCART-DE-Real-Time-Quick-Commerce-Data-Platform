# What this does
# -> Validation layer.
# Admin sends: JSON {}
# Pydantic validates schema before service logic.

from pydantic import BaseModel

class ProductCreate(BaseModel):
    """
    Admin product creation payload
    """
    product_id: str
    product_name: str
    category: str
    price: float
    stock_qty: int


class ProductPriceUpdate(BaseModel):
    """
    Product price update payload
    """
    price: float


class ProductInventoryUpdate(BaseModel):
    """
    Inventory update payload
    """
    stock_qty: int