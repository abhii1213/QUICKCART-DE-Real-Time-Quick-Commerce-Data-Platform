import uuid

from event_api.db.postgres import SessionLocal
from event_api.db.models import Product, Order, OrderItem


def create_order(user_id, order_data):
    """
    Create customer order transaction

    Steps:
    1. Validate products
    2. Validate stock
    3. Create order
    4. Create order items
    5. Reduce inventory
    6. Commit transaction
    """

    db = SessionLocal()

    try:
        total_amount = 0
        processed_items = []
        updated_inventory = []

        # Validate all products first
        for item in order_data.items:
            product = db.query(Product).filter(
                Product.product_id == item.product_id,
                Product.is_active == True
            ).first()

            if not product:
                db.close()
                return None, "Product not found"

            if product.stock_qty < item.qty:
                db.close()
                return None, "Insufficient stock"

            line_total = product.price * item.qty
            total_amount += line_total

            # Store plain Python data (NOT ORM objects)
            processed_items.append({
                "product_id": product.product_id,
                "product_name": product.product_name,
                "qty": item.qty,
                "unit_price": product.price,
                "line_total": line_total,
                "product_ref": product   # internal DB update only
            })

        order_id = str(uuid.uuid4())

        # Create order master
        order = Order(
            order_id=order_id,
            user_id=user_id,
            total_amount=total_amount,
            payment_mode=order_data.payment_mode,
            order_status="PLACED"
        )

        db.add(order)

        # Create order items + reduce stock
        for item in processed_items:
            order_item = OrderItem(
                order_id=order_id,
                product_id=item["product_id"],
                qty=item["qty"],
                unit_price=item["unit_price"],
                line_total=item["line_total"]
            )

            db.add(order_item)

            # reduce inventory
            item["product_ref"].stock_qty -= item["qty"]
            updated_inventory.append({
                "product_id": item["product_id"],
                "stock_qty": item["product_ref"].stock_qty
            })

        db.commit()

        db.close()

        return {
            "order_id": order_id,
            "total_amount": total_amount,
            "items": processed_items,
            "updated_inventory": updated_inventory
        }, None

    except Exception as e:
        db.rollback()
        db.close()
        return None, str(e)