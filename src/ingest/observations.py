from psycopg.types.json import Jsonb

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
    with connection.cursor() as cursor:
        cursor.executemany(query, rows)