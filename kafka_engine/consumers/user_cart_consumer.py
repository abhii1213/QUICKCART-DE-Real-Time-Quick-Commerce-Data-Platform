from kafka import KafkaConsumer
import json
from datetime import datetime, UTC
from warehouse.databricks_writer import DatabricksWriter


def start_consumer():
    """
    Consumer for Users Pre-Checkout Activity

    Handles:
        CART_ITEM_ADDED
        CART_ITEM_REMOVED
        CART_QTY_INCREASED
        CART_QTY_DECREASED
        CHECKOUT_STARTED

    Responsibilities:
    - Process customer Pre-Checkout activity

    Target Table:
    quickcart_bronze.bronze_cart_events
    """

    consumer = KafkaConsumer(
        "user_cart_events",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="user_auth_events-group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

    db_writer = DatabricksWriter()

    print("User_Cart_Events Consumer Started...")

    for message in consumer:
        event = message.value

        processed_event = {
            **event,
            "processing_ts": datetime.now(UTC).isoformat(),
            "consumer_name": "user_cart_events_consumer",
            "processing_status": "SUCCESS"
        }

        print("\nProcessed User Cart Events:")
        print(json.dumps(processed_event, indent=2))

        try:
            db_writer.insert_event("bronze_cart_events", processed_event)
        except Exception as e:
            print("Databricks Insert Failed:", str(e))