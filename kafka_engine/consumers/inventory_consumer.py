from kafka import KafkaConsumer
import json
from datetime import datetime

# Consumer for inventory updates
# Purpose: Consume stock/inventory updates.
# Handles:
# - INVENTORY_UPDATED

consumer = KafkaConsumer(
    "inventory_events",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="inventory-consumer-group",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

print("Inventory Consumer Started... Listening to inventory_events...")

for message in consumer:
    event = message.value

    # Add stream processing metadata
    processed_event = {
        **event,
        "processing_ts": datetime.utcnow().isoformat(),
        "consumer_name": "inventory_consumer",
        "processing_status": "SUCCESS"
    }

    print("\nProcessed Inventory Event:")
    print(json.dumps(processed_event, indent=2))