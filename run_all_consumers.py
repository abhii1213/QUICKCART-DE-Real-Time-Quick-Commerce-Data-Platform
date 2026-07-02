import threading
import time

from kafka_engine.consumers.cart_consumer import start_consumer as start_cart
from kafka_engine.consumers.activity_consumer import start_consumer as start_activity
from kafka_engine.consumers.products_cdc_consumer import start_consumer as products_cdc
from kafka_engine.consumers.orders_cdc_consumer import start_consumer as orders_cdc
from kafka_engine.consumers.order_items_cdc_consumer import start_consumer as order_items_cdc


def launch(target, name):
    """
    Start a consumer in its own thread
    """
    thread = threading.Thread(target=target, name=name, daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    print("Starting all Kafka consumers...")

    threads = [
        # launch(start_order, "order-consumer"),
        # launch(start_product, "product-consumer"),
        # launch(start_inventory, "inventory-consumer"),
        launch(start_cart, "cart-consumer"),
        launch(start_activity, "activity-consumer"),
        launch(products_cdc, "product-cdc-consumer"),
        launch(orders_cdc, "order-cdc-consumer"),
        launch(order_items_cdc, "order-items-cdc-consumer")
    ]

    print("All consumers running. Press CTRL + C to stop.")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping all consumers...")
        print("Shutdown complete.")