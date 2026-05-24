from kafka import KafkaConsumer
import json
from datetime import datetime, UTC
from warehouse.databricks_writer import DatabricksWriter


def start_consumer():
    """
    Consumer for customer browsing/activity events

    Handles:
    - PRODUCT_SEARCHED
    - PRODUCT_VIEWED
    - CHECKOUT_STARTED

    Responsibilities:
    - Process customer engagement events
    - Enrich activity records
    - Persist Bronze activity events

    Target Table:
    quickcart_bronze.bronze_activity_events
    """

    consumer = KafkaConsumer(
        "user_activity_events",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="activity-consumer-group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

    db_writer = DatabricksWriter()

    print("Activity Consumer Started...")

    for message in consumer:
        event = message.value

        processed_event = {
            **event,
            "processing_ts": datetime.now(UTC).isoformat(),
            "consumer_name": "activity_consumer",
            "processing_status": "SUCCESS"
        }

        print("\nProcessed Activity Event:")
        print(json.dumps(processed_event, indent=2))

        try:
            db_writer.insert_event("bronze_activity_events", processed_event)
        except Exception as e:
            print("Databricks Insert Failed:", str(e))