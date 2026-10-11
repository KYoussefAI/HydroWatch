import psycopg
from psycopg.types.json import Jsonb

import os
from dotenv import load_dotenv

from datetime import datetime, timezone, timedelta
import uuid

from usgs_client import fetch_url, get_next_url, save_raw_json

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

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=1)
    date_range = (
        f"{start.strftime('%Y-%m-%dT%H:%M:%SZ')}/"
        f"{end.strftime('%Y-%m-%dT%H:%M:%SZ')}"
    )
    date_range = os.getenv("USGS_DATETIME") or date_range

    url = "collections/continuous/items"
    params = {
        "monitoring_location_id": "USGS-06115200,USGS-06066500,USGS-06052500",
        "parameter_code": "00060,00065,00010",
        "datetime": date_range, # for testing purposes
        "limit": 500
    }
    page_number = 0
    all_rows = []

    while url:
        data = fetch_url(
            url,
            params 
        )
        extracted_at = datetime.now(timezone.utc)
        page_number += 1

        save_raw_json(data,batch_id,page_number)

        rows = prepare_observations(data,extracted_at,batch_id) 
        all_rows.extend(rows)

        print(f"Page {page_number}: {len(rows)} observations")

        url = get_next_url(data)
        params = None

    if all_rows:
        connection = connect_db()

        try:
            insert_observations(connection,all_rows)
        finally :
            connection.close()

        print(f"Inserted : {len(all_rows)} observations\
            | batch_id : {batch_id}\
            | extracted_at : {extracted_at}")


if __name__ == "__main__":
    main()