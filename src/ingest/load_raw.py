import psycopg
from psycopg.types.json import Jsonb

import os
from dotenv import load_dotenv

from datetime import datetime,timezone
import uuid

from usgs_client import fetch_url, save_raw_json

load_dotenv()

def connect_db():
    return psycopg.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

# connection = connect_db()
# print("connected")
# connection.close()


def prepare_observations(data,extracted_at,batch_id):
    rows = []
    features = data["features"]
    for feature in features :
        p = feature["properties"]
        geometry = feature["geometry"]
        rows.append((
            feature["id"],
            p["time_series_id"],
            p["monitoring_location_id"],
            p["parameter_code"],
            p["statistic_id"],
            p["time"],
            p["value"],
            p["unit_of_measure"],
            p["approval_status"],
            p["qualifier"],
            p["last_modified"],
            p["method_category"],
            Jsonb(geometry),
            extracted_at,
            batch_id,
        ))
        
    return rows


def insert_observations(connection, rows):

    query = """
        INSERT INTO raw.observations (
            source_id,
            time_series_id,
            monitoring_location_id,
            parameter_code,
            statistic_id,
            observation_time,
            value,
            unit_of_measure,
            approval_status,
            qualifier,
            last_modified,
            method_category,
            geometry,
            extracted_at,
            load_batch_id
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
    """

    try :
        with connection.cursor() as cursor:
            cursor.executemany(query, rows)

        connection.commit()
    except Exception :
        connection.rollback()
        raise


def main():
    batch_id = str(uuid.uuid4())

    params = {
        "monitoring_location_id": "USGS-06115200,USGS-06066500,USGS-06052500",
        "parameter_code": "00060,00065,00010",
        "limit": 500
    }

    data = fetch_url(
        "collections/continuous/items",
        params
    )

    extracted_at = datetime.now(timezone.utc)

    save_raw_json(data,batch_id)

    rows = prepare_observations(data,extracted_at,batch_id)

    connection = connect_db()
    try:
        insert_observations(connection,rows)
    finally :
        connection.close()

    print(f"Inserted : {len(rows)} observations \
          | batch_id : {batch_id} \
          | extracted_at : {extracted_at}")


if __name__ == "__main__":
    main()
