import sys
import os
from kafka import KafkaConsumer
from datetime import datetime, UTC
import json

from warehouse.databricks_writer import DatabricksWriter


def start_consumer():
    """
    ==========================================================
    ORDER ITEMS CDC CONSUMER

    Source:
        quickcart.public.order_items

    Purpose:
        Capture every order line item change

    Example:

        Order A
            Product 101
            Qty 2

        Order A
            Product 102
            Qty 1

    Target:
        bronze_order_items_cdc

    Architecture:

        PostgreSQL
             ↓
        Debezium CDC
             ↓
        quickcart.public.order_items
             ↓
        order_items_cdc_consumer
             ↓
        bronze_order_items_cdc

    ==========================================================
    """

    # 1. Initialize Kafka Consumer
    consumer = KafkaConsumer(
        "quickcart.public.order_items",
        bootstrap_servers="localhost:9092",
        
        # 'earliest' ensures no line items are missed if the consumer restarts
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="order-items-cdc-group",
        
        # Automatically parse the JSON byte stream
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

    db_writer = DatabricksWriter()

    print("Order Items CDC Consumer Started...")

    # 2. Listen for database changes
    for message in consumer:

        event = message.value

        # Extract the main Debezium payload envelope
        payload = event.get("payload")
        if not payload:
            continue

        # 'after' contains the current state of the order line item
        after = payload.get("after")

        # Delete/Tombstone protection
        # If an item is removed from a cart/order, 'after' is null. 
        if not after:
            continue

        # 'source' contains transaction log metadata from PostgreSQL
        source = payload.get("source")

        # 3. Flatten the record for the Databricks Bronze layer
        record = {
            # --- Relational & Business Data ---
            "order_item_id": after.get("order_item_id"), # Primary Key
            "order_id": after.get("order_id"),           # Foreign Key to Orders
            "product_id": after.get("product_id"),       # Foreign Key to Products
            "qty": after.get("qty"),
            "unit_price": after.get("unit_price"),
            "line_total": after.get("line_total"),

            # --- CDC Metadata ---
            # 'op' will typically be 'c' (create) for a new line item, 
            # or 'u' (update) if the quantity is changed.
            "op": payload.get("op"),

            # Postgres transaction timestamp converted to ISO format
            "source_ts": datetime.fromtimestamp(
                payload["ts_ms"] / 1000,
                UTC
            ).isoformat(),

            "tx_id": source.get("txId"),

            # Log Sequence Number (LSN) - Used for deterministic deduplication in PySpark
            "lsn": source.get("lsn"),

            # Pipeline processing timestamp
            "ingestion_ts": datetime.now(UTC).isoformat()
        }

        print("\nProcessed Order Item CDC:")

        print(
            json.dumps(
                record,
                indent=2,
                default=str
            )
        )

        # 4. Insert into Databricks Delta Table
        try:
            db_writer.insert_cdc_record(
                "bronze_order_items_cdc",
                record
            )

        except Exception as e:
            print(
                "Databricks Insert Failed:",
                str(e)
            )