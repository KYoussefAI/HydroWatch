from psycopg.types.json import Jsonb


def prepare_metadata(data, extracted_at, batch_id):
    rows = []

    for feature in data["features"]:
        rows.append((
            feature["id"],
            Jsonb(feature),
            extracted_at,
            batch_id
        ))

    return rows


def insert_metadata(connection, rows, table_name):
    queries = {
        "stations": """
            INSERT INTO raw.stations
            (source_id, payload, extracted_at, load_batch_id)
            VALUES (%s, %s, %s, %s)
        """,
        "parameters": """
            INSERT INTO raw.parameters
            (source_id, payload, extracted_at, load_batch_id)
            VALUES (%s, %s, %s, %s)
        """
    }

    with connection.cursor() as cursor:
        cursor.executemany(queries[table_name], rows)