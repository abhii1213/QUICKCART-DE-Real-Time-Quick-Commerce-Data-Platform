from kafka import KafkaConsumer
import json
from datetime import datetime, UTC
from warehouse.databricks_writer import DatabricksWriter


def start_consumer():
    """
    Consumer for product catalog events

    Handles:
    - PRODUCT_CREATED
    - PRICE_UPDATED
    - PRODUCT_DELISTED
    - FLASH_SALE_STARTED

    Responsibilities:
    - Consume product catalog change events
    - Enrich processed records
    - Persist Bronze product events

    Target Table:
    quickcart_bronze.bronze_product_events
    """

    consumer = KafkaConsumer(
        "product_events",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="product-consumer-group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

    db_writer = DatabricksWriter()

    print("Product Consumer Started...")

    for message in consumer:
        event = message.value

        processed_event = {
            **event,
            "processing_ts": datetime.now(UTC).isoformat(),
            "consumer_name": "product_consumer",
            "processing_status": "SUCCESS"
        }

        print("\nProcessed Product Event:")
        print(json.dumps(processed_event, indent=2))

        try:
            db_writer.insert_event("bronze_product_events", processed_event)
        except Exception as e:
            print("Databricks Insert Failed:", str(e))