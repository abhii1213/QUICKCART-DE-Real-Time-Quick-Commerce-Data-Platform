from kafka import KafkaConsumer
import json
from datetime import datetime

# Consumer for customer activity events
# Purpose: Consume browsing/search/checkout behavior
# Handles:
# - PRODUCT_VIEWED
# - PRODUCT_SEARCHED
# - CHECKOUT_STARTED

consumer = KafkaConsumer(
    "user_activity_events",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="activity-consumer-group",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

print("Activity Consumer Started... Listening to user_activity_events...")

for message in consumer:
    event = message.value

    # Enrich event for downstream processing
    processed_event = {
        **event,
        "processing_ts": datetime.utcnow().isoformat(),
        "consumer_name": "activity_consumer",
        "processing_status": "SUCCESS"
    }

    print("\nProcessed Activity Event:")
    print(json.dumps(processed_event, indent=2))