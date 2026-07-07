from kafka import KafkaConsumer
import json
from datetime import datetime, UTC
from warehouse.databricks_writer import DatabricksWriter


def start_consumer():
    """
    Consumer for customer Discovery & Intent events

    Handles:
    - PRODUCT_SEARCHED
    - PRODUCT_VIEWED
    - OUT_OF_STOCK_INTEREST

    Responsibilities:
    - Process customer activities when a user searches or views any product
    - OUT_OF_STOCK_INTEREST - process when a user clicks on a product that is out of stock

    Target Table:
    quickcart_bronze.bronze_browsing_events
    """

    consumer = KafkaConsumer(
        "user_browsing_events",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="user_browsing_events-group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

    db_writer = DatabricksWriter()

    print("Browsing_Events Consumer Started...")

    for message in consumer:
        event = message.value

        processed_event = {
            **event,
            "processing_ts": datetime.now(UTC).isoformat(),
            "consumer_name": "user_browsing_events_consumer",
            "processing_status": "SUCCESS"
        }

        print("\nProcessed User Browsing Events:")
        print(json.dumps(processed_event, indent=2))

        try:
            db_writer.insert_event("bronze_browsing_events", processed_event)
        except Exception as e:
            print("Databricks Insert Failed:", str(e))