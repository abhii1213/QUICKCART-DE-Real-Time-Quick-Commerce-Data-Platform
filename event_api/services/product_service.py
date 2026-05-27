# This is business logic layer.
# Responsibilities:
# create product
# fetch products
# update price
# update inventory
# soft delete


from event_api.db.postgres import SessionLocal
from event_api.db.models import Product


def create_product(product_data):
    """
    Insert new product into PostgreSQL
    """

    db = SessionLocal()

    product = Product(
        product_id=product_data.product_id,
        product_name=product_data.product_name,
        category=product_data.category,
        price=product_data.price,
        stock_qty=product_data.stock_qty,
        is_active=True
    )

    db.add(product)
    db.commit()
    db.close()

    return product


def get_active_products():
    """
    Fetch customer-visible active products
    """

    db = SessionLocal()

    products = db.query(Product).filter(
        Product.is_active == True
    ).all()

    db.close()

    return products


def update_product_price(product_id, new_price):
    """
    Update product pricing
    """

    db = SessionLocal()

    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if product:
        product.price = new_price
        db.commit()

    db.close()

    return product


def update_inventory(product_id, stock_qty):
    """
    Update stock quantity
    """

    db = SessionLocal()

    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if product:
        product.stock_qty = stock_qty
        db.commit()

    db.close()

    return product


def deactivate_product(product_id):
    """
    Soft delete / delist product
    """

    db = SessionLocal()

    product = db.query(Product).filter(
        Product.product_id == product_id
    ).first()

    if product:
        product.is_active = False
        db.commit()

    db.close()

    return product