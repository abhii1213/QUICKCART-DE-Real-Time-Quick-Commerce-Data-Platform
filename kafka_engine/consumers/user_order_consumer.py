from kafka import KafkaConsumer
import json
from datetime import datetime, UTC
from warehouse.databricks_writer import DatabricksWriter


def start_consumer():
    """
    Consumer for Users when they places their orders Activity

    Handles:
        ORDER_PLACED

    Responsibilities:
    - Process customer Orders activity

    Target Table:
    quickcart_bronze.bronze_order_events
    """

    consumer = KafkaConsumer(
        "user_order_events",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="user_auth_events-group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

    db_writer = DatabricksWriter()

    print("User_Order_Events Consumer Started...")

    for message in consumer:
        event = message.value

        processed_event = {
            **event,
            "processing_ts": datetime.now(UTC).isoformat(),
            "consumer_name": "user_cart_events_consumer",
            "processing_status": "SUCCESS"
        }

        print("\nProcessed User Order Events:")
        print(json.dumps(processed_event, indent=2))

        try:
            db_writer.insert_event("bronze_order_events", processed_event)
        except Exception as e:
            print("Databricks Insert Failed:", str(e))