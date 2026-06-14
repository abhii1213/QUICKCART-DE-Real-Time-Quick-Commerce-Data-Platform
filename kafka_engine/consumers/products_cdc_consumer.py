from kafka import KafkaConsumer
from datetime import datetime, UTC
import json

from warehouse.databricks_writer import DatabricksWriter


def start_consumer():

    consumer = KafkaConsumer(
        "quickcart.public.products",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="products-cdc-group",
        value_deserializer=lambda x: json.loads(
            x.decode("utf-8")
        )
    )

    db_writer = DatabricksWriter()

    print("Products CDC Consumer Started...")

    for message in consumer:

        event = message.value

        payload = event.get("payload")

        if not payload:
            continue

        after = payload.get("after")

        if not after:
            continue

        source = payload.get("source")

        record = {

            "product_id":
                after.get("product_id"),

            "product_name":
                after.get("product_name"),

            "category":
                after.get("category"),

            "price":
                after.get("price"),

            "stock_qty":
                after.get("stock_qty"),

            "is_active":
                after.get("is_active"),

            "op":
                payload.get("op"),

            "source_ts":
                datetime.fromtimestamp(
                    payload["ts_ms"] / 1000,
                    UTC
                ).isoformat(),

            "tx_id":
                source.get("txId"),

            "lsn":
                source.get("lsn"),

            "ingestion_ts":
                datetime.now(
                    UTC
                ).isoformat()
        }

        print(
            "\nProcessed Product CDC:"
        )

        print(
            json.dumps(
                record,
                indent=2,
                default=str
            )
        )

        try:

            db_writer.insert_cdc_record(
                "bronze_products_cdc",
                record
            )

        except Exception as e:

            print(
                "Databricks Insert Failed:",
                str(e)
            )