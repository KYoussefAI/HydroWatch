from datetime import datetime, timezone, timedelta
import uuid
import os

from usgs_client import fetch_url, get_next_url, save_raw_json
from observations import prepare_observations, insert_observations
from metadata import prepare_metadata, insert_metadata

from db import connect_db


def main():
    batch_id = str(uuid.uuid4())

    station_ids = "USGS-06115200,USGS-06066500,USGS-06052500"
    parameter_ids = "00060,00065,00010"

    # Automatic or historical date window
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=1)

    date_range = (
        f"{start.strftime('%Y-%m-%dT%H:%M:%SZ')}/"
        f"{end.strftime('%Y-%m-%dT%H:%M:%SZ')}"
    )

    date_range = os.getenv("USGS_DATETIME") or date_range

    # OBSERVATIONS
    url = "collections/continuous/items"
    params = {
        "monitoring_location_id": station_ids,
        "parameter_code": parameter_ids,
        "datetime": date_range,
        "limit": 500
    }

    page_number = 0
    observation_rows = []

    while url:
        data = fetch_url(url, params)

        extracted_at = datetime.now(timezone.utc)
        page_number += 1

        save_raw_json(data, batch_id, page_number)

        rows = prepare_observations(data, extracted_at, batch_id)
        observation_rows.extend(rows)

        print(f"Observations page {page_number}: {len(rows)} rows")

        url = get_next_url(data)
        params = None

    # STATIONS
    stations_data = fetch_url(
        "collections/monitoring-locations/items",
        {"id": station_ids, "limit": 10}
    )

    stations_extracted_at = datetime.now(timezone.utc)
    save_raw_json(stations_data, batch_id, 1, "stations")

    station_rows = prepare_metadata(
        stations_data, stations_extracted_at, batch_id
    )

    # PARAMETERS
    parameters_data = fetch_url(
        "collections/parameter-codes/items",
        {"id": parameter_ids, "limit": 10}
    )

    parameters_extracted_at = datetime.now(timezone.utc)
    save_raw_json(parameters_data, batch_id, 1, "parameters")

    parameter_rows = prepare_metadata(
        parameters_data, parameters_extracted_at, batch_id
    )

    # Validate metadata before loading
    if len(station_rows) != 3 or len(parameter_rows) != 3:
        raise ValueError(
            "Expected 3 stations and 3 parameters. "
            f"Received {len(station_rows)} stations "
            f"and {len(parameter_rows)} parameters."
        )

    connection = connect_db()

    try:
        insert_observations(connection, observation_rows)
        insert_metadata(connection, station_rows, "stations")
        insert_metadata(connection, parameter_rows, "parameters")

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    print(
        f"Batch: {batch_id} | "
        f"Observations: {len(observation_rows)} | "
        f"Stations: {len(station_rows)} | "
        f"Parameters: {len(parameter_rows)}"
    )


if __name__ == "__main__":
    main()