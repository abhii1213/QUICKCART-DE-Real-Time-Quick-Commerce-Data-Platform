from kafka import KafkaConsumer
import json
from datetime import datetime, UTC
from warehouse.databricks_writer import DatabricksWriter


def start_consumer():
    """
    Consumer for order lifecycle events

    Handles:
    - ORDER_PLACED
    - ORDER_CANCELLED

    Responsibilities:
    - Read order events from Kafka
    - Deserialize JSON messages
    - Enrich events with processing metadata
    - Persist processed records into Databricks Bronze

    Target Table:
    quickcart_bronze.bronze_order_events
    """

    # Initialize the Kafka Consumer
    consumer = KafkaConsumer(
        "order_events",   # The topic we want to listen to
        bootstrap_servers="localhost:9092",
        auto_offset_reset="latest",   # consume only new events
        enable_auto_commit=True,  # Kafka will automatically remember which messages this consumer has already read
        group_id="order-consumer-group", # Consumers with the same group_id share the workload. If you spin up a second. script with this ID, Kafka splits the messages between them.
        # Kafka sends bytes. This reverses what the producer did: 
        # it decodes the utf-8 bytes back into a JSON string, then into a Python dictionary.
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

    db_writer = DatabricksWriter()

    print("Order Consumer Started...")

    # This is a continuous, blocking loop. It stays awake waiting for new messages.
    for message in consumer:
        event = message.value  # Extract the actual Python dictionary payload from the Kafka message envelope

        # Add stream processing metadata
        processed_event = {
            **event, # Unpack all the original event data
            "processing_ts": datetime.now(UTC).isoformat(), # Add a timestamp
            "consumer_name": "order_consumer",  # Track which system processed it
            "processing_status": "SUCCESS"
        }

        print("\nProcessed Order Event:")
        print(json.dumps(processed_event, indent=2))

        try:
            db_writer.insert_event("bronze_order_events", processed_event)
        except Exception as e:
            print("Databricks Insert Failed:", str(e))