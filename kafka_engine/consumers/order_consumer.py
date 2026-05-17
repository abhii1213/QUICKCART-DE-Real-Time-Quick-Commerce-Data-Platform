from kafka import KafkaConsumer
import json
from datetime import datetime

# Consumer for order lifecycle events
# Handles:
# - ORDER_PLACED
# - ORDER_CANCELLED
# Future:
# - ORDER_CONFIRMED
# - ORDER_PACKED
# - DELIVERED

# Initialize the Kafka Consumer
consumer = KafkaConsumer(
    "order_events", # The topic we want to listen to
    bootstrap_servers="localhost:9092",
    
    # "earliest" means if this consumer has never run before, it will read all 
    # historical messages from the beginning of the topic.
    auto_offset_reset="earliest", 
    
    # Kafka will automatically remember which messages this consumer has already read
    enable_auto_commit=True, 
    
    # Consumers with the same group_id share the workload. If you spin up a second 
    # script with this ID, Kafka splits the messages between them.
    group_id="order-consumer-group",
    
    # Kafka sends bytes. This reverses what the producer did: 
    # it decodes the utf-8 bytes back into a JSON string, then into a Python dictionary.
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

print("Order Consumer Started... Listening to order_events...")

# This is a continuous, blocking loop. It stays awake waiting for new messages.
for message in consumer:
    # Extract the actual Python dictionary payload from the Kafka message envelope
    event = message.value

    # Simulate basic stream processing by enriching the data
    processed_event = {
        **event, # Unpack all the original event data
        "processing_ts": datetime.utcnow().isoformat(), # Add a timestamp
        "consumer_name": "order_consumer",              # Track which system processed it
        "processing_status": "SUCCESS"
    }

    print("\nProcessed Order Event:")
    print(json.dumps(processed_event, indent=2))