"""Reload a previously archived USGS extraction as a new PostgreSQL batch."""

import argparse
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from db import connect_db
from metadata import insert_metadata, prepare_metadata
from observations import insert_observations, prepare_observations

BATCH_PATTERN = re.compile(r"^[0-9a-fA-F-]{36}$")
PAGE_PATTERN = re.compile(r"_page_(\d+)\.json$")


def load_pages(dataset, original_batch_id):
    folder = Path("data/raw") / dataset
    paths = sorted(
        folder.glob(f"{dataset}_*_{original_batch_id}_page_*.json"),
        key=lambda p: int(PAGE_PATTERN.search(p.name).group(1))
    )
    if not paths:
        raise FileNotFoundError(f"No archived {dataset} files for {original_batch_id}")

    page_numbers = [int(PAGE_PATTERN.search(p.name).group(1)) for p in paths]
    if page_numbers != list(range(1, len(paths) + 1)):
        raise ValueError(f"Missing or duplicate {dataset} page numbers: {page_numbers}")

    return [json.loads(path.read_text(encoding="utf-8")) for path in paths]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch_id", help="Original extraction batch UUID")
    parser.add_argument("--apply", action="store_true", help="Insert rows (default: dry run)")
    args = parser.parse_args()

    if not BATCH_PATTERN.fullmatch(args.batch_id):
        parser.error("Expected a UUID batch ID")
    source_batch_id = str(uuid.UUID(args.batch_id))

    observations = load_pages("observations", source_batch_id)
    stations = load_pages("stations", source_batch_id)
    parameters = load_pages("parameters", source_batch_id)

    if len(stations) != 1 or len(parameters) != 1:
        raise ValueError("Expected one archived page each for stations and parameters")

    counts = {
        "observations": sum(len(page["features"]) for page in observations),
        "stations": len(stations[0]["features"]),
        "parameters": len(parameters[0]["features"]),
    }
    print(f"Archive batch: {source_batch_id} | {counts}")

    if not args.apply:
        print("Dry run only. Add --apply to write a new database batch.")
        return

    replay_batch_id = str(uuid.uuid4())
    replayed_at = datetime.now(timezone.utc)
    observation_rows = [
        row
        for page in observations
        for row in prepare_observations(page, replayed_at, replay_batch_id)
    ]
    station_rows = prepare_metadata(stations[0], replayed_at, replay_batch_id)
    parameter_rows = prepare_metadata(parameters[0], replayed_at, replay_batch_id)

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

    print(f"Replayed archive {source_batch_id} as new batch {replay_batch_id}")


if __name__ == "__main__":
    main()
