import threading
import time

from kafka_engine.consumers.order_consumer import start_consumer as start_order
from kafka_engine.consumers.product_consumer import start_consumer as start_product
from kafka_engine.consumers.inventory_consumer import start_consumer as start_inventory
from kafka_engine.consumers.cart_consumer import start_consumer as start_cart
from kafka_engine.consumers.activity_consumer import start_consumer as start_activity


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
        launch(start_order, "order-consumer"),
        launch(start_product, "product-consumer"),
        launch(start_inventory, "inventory-consumer"),
        launch(start_cart, "cart-consumer"),
        launch(start_activity, "activity-consumer")
    ]

    print("All consumers running. Press CTRL + C to stop.")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping all consumers...")
        print("Shutdown complete.")