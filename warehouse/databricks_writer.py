import os
import json
from databricks import sql
from dotenv import load_dotenv

# Load secrets from .env
load_dotenv()


class DatabricksWriter:
    """
    Reusable utility for writing processed events into Bronze tables
    """

    def __init__(self):
        self.server_hostname = os.getenv("DATABRICKS_SERVER_HOSTNAME")
        self.http_path = os.getenv("DATABRICKS_HTTP_PATH")
        self.access_token = os.getenv("DATABRICKS_ACCESS_TOKEN")

    def _connect(self):
        """
        Create Databricks SQL connection
        """
        return sql.connect(
            server_hostname=self.server_hostname,
            http_path=self.http_path,
            access_token=self.access_token
        )

    def insert_event(self, table_name: str, event: dict):
        """
        Generic Bronze event insert
        """

        connection = self._connect()
        cursor = connection.cursor()

        insert_query = f"""
        INSERT INTO quickcart_de.quickcart_bronze.{table_name} (
            event_id,
            event_type,
            event_version,
            event_ts,
            source_system,
            payload,
            processing_ts,
            consumer_name,
            processing_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(
            insert_query,
            (
                event["event_id"],
                event["event_type"],
                event["event_version"],
                event["event_ts"],
                event["source_system"],
                json.dumps(event["payload"]),
                event["processing_ts"],
                event["consumer_name"],
                event["processing_status"]
            )
        )

        connection.commit()
        cursor.close()
        connection.close()

        print(f"Inserted into Databricks Bronze: {table_name}")


    def insert_cdc_record(
        self,
        table_name: str,
        record: dict
    ):
        # Generic CDC table insert
        connection = self._connect()
        cursor = connection.cursor()

        columns = ", ".join(record.keys())

        placeholders = ", ".join(
            ["?"] * len(record)
        )

        query = f"""
        INSERT INTO quickcart_de.quickcart_bronze.{table_name}
        ({columns})
        VALUES ({placeholders})
        """

        cursor.execute(
            query,
            tuple(record.values())
        )

        connection.commit()

        cursor.close()
        connection.close()

        print(
            f"Inserted into Databricks Bronze: {table_name}"
        )