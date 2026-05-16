from kafka import KafkaProducer
import json

# Initialize the Kafka Producer
producer = KafkaProducer(
    # The address of your Kafka broker (running locally on port 9092)
    bootstrap_servers="localhost:9092",
    # Kafka only accepts bytes. This automatically converts our Python dictionaries (v)
    # into a JSON string, and then encodes that string into utf-8 bytes before sending.
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


def publish_event(topic: str, event: dict):
    """Sends a JSON event to a specific Kafka topic."""
    
    # Adds the event to an internal buffer, ready to be sent
    producer.send(topic, event)
    
    # Forces the producer to immediately send all buffered messages to the broker.
    # (Note: This is great for testing/scripts, but in high-volume production streams, 
    # you usually let Kafka handle flushing automatically for better performance).
    producer.flush()

    print(f"Published to Kafka topic: {topic}")