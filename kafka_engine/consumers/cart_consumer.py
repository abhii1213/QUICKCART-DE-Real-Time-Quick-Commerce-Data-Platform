from kafka import KafkaConsumer
import json
from datetime import datetime

# Consumer for cart activity
# Purpose: Consume cart actions
# Handles:
# - ADD_TO_CART
# - REMOVE_FROM_CART

consumer = KafkaConsumer(
    "cart_events",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="cart-consumer-group",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

print("Cart Consumer Started... Listening to cart_events...")

for message in consumer:
    event = message.value

    # Add processing metadata
    processed_event = {
        **event,
        "processing_ts": datetime.utcnow().isoformat(),
        "consumer_name": "cart_consumer",
        "processing_status": "SUCCESS"
    }

    print("\nProcessed Cart Event:")
    print(json.dumps(processed_event, indent=2))