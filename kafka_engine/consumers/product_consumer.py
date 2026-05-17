from kafka import KafkaConsumer
import json
from datetime import datetime

# Consumer for product-related events
# Purpose: Consume product/admin events like create, price update, delist.
# Handles:
# - PRODUCT_CREATED
# - PRICE_UPDATED
# - PRODUCT_DELISTED

consumer = KafkaConsumer(
    "product_events",   # Kafka topic to subscribe to
    bootstrap_servers="localhost:9092",   # Kafka broker address
    auto_offset_reset="earliest",   # Read existing messages if no committed offset
    enable_auto_commit=True,   # Automatically commit offsets after processing
    group_id="product-consumer-group",   # Consumer group identifier
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))   # Convert bytes -> Python dict
)

print("Product Consumer Started... Listening to product_events...")

# Continuously listen for incoming Kafka messages
for message in consumer:
    event = message.value

    # Enrich event with processing metadata
    processed_event = {
        **event,
        "processing_ts": datetime.utcnow().isoformat(),   # Processing timestamp
        "consumer_name": "product_consumer",              # Which consumer processed it
        "processing_status": "SUCCESS"                    # Processing status
    }

    print("\nProcessed Product Event:")
    print(json.dumps(processed_event, indent=2))