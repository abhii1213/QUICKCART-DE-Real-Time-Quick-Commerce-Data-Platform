import sys
import os
from kafka import KafkaConsumer
from datetime import datetime, UTC
import json

from warehouse.databricks_writer import DatabricksWriter


def start_consumer():
    """
    ==========================================================
    ORDERS CDC CONSUMER

    Source:
        quickcart.public.orders

    Purpose:
        Capture all order changes from PostgreSQL CDC

    Debezium Operations:
        c = Create
        u = Update
        d = Delete

    Target:
        bronze_orders_cdc
    ==========================================================
    """

    # 1. Initialize Kafka Consumer
    consumer = KafkaConsumer(
        "quickcart.public.orders",
        bootstrap_servers="localhost:9092",
        
        # 'earliest' ensures we process all historical orders in the topic 
        # if the consumer crashes and restarts.
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="orders-cdc-group",
        
        # Automatically convert the raw byte stream into a Python dictionary
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

    db_writer = DatabricksWriter()

    print("Orders CDC Consumer Started...")

    # 2. Continuously listen for new database events
    for message in consumer:

        event = message.value

        # Debezium wraps all data and metadata inside the 'payload' object
        payload = event.get("payload")
        if not payload:
            continue

        # 'after' represents the new state of the row in PostgreSQL
        after = payload.get("after")

        # Delete/Tombstone protection:
        # If an order is hard-deleted, 'after' will be null. We skip these for now.
        if not after:
            continue

        # 'source' contains the PostgreSQL transaction logs
        source = payload.get("source")

        # 3. Build the flattened Bronze record
        record = {
            # --- Business Data ---
            "order_id": after.get("order_id"),
            "user_id": after.get("user_id"),
            "total_amount": after.get("total_amount"),
            "payment_mode": after.get("payment_mode"),
            "order_status": after.get("order_status"),
            "created_at": after.get("created_at"),

            # --- CDC Metadata ---
            # 'op' tells us if this was a new order ('c') or an updated status ('u')
            "op": payload.get("op"),

            # Convert Postgres transaction time to ISO format
            "source_ts": datetime.fromtimestamp(
                payload["ts_ms"] / 1000,
                UTC
            ).isoformat(),

            # Database transaction ID
            "tx_id": source.get("txId"),

            # Log Sequence Number (LSN) - Essential for deduplicating updates later in PySpark
            "lsn": source.get("lsn"),

            # Pipeline metadata: Exact time this script processed the record
            "ingestion_ts": datetime.now(UTC).isoformat()
        }

        print("\nProcessed Order CDC:")
        print(
            json.dumps(
                record,
                indent=2,
                default=str
            )
        )

        # 4. Push to Databricks Bronze Layer
        try:
            db_writer.insert_cdc_record(
                "bronze_orders_cdc",
                record
            )
        except Exception as e:
            print("Databricks Insert Failed:", str(e))