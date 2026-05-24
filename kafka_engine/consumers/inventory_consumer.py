from kafka import KafkaConsumer
import json
from datetime import datetime, UTC
from warehouse.databricks_writer import DatabricksWriter


def start_consumer():
    """
    Consumer for inventory stock events

    Handles:
    - INVENTORY_UPDATED

    Responsibilities:
    - Process stock update events
    - Enrich inventory records
    - Persist Bronze inventory events

    Target Table:
    quickcart_bronze.bronze_inventory_events
    """

    consumer = KafkaConsumer(
        "inventory_events",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="inventory-consumer-group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

    db_writer = DatabricksWriter()

    print("Inventory Consumer Started...")

    for message in consumer:
        event = message.value

        processed_event = {
            **event,
            "processing_ts": datetime.now(UTC).isoformat(),
            "consumer_name": "inventory_consumer",
            "processing_status": "SUCCESS"
        }

        print("\nProcessed Inventory Event:")
        print(json.dumps(processed_event, indent=2))

        try:
            db_writer.insert_event("bronze_inventory_events", processed_event)
        except Exception as e:
            print("Databricks Insert Failed:", str(e))