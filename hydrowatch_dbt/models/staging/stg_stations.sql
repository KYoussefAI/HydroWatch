select
    raw_id,
    source_id as station_id,
    payload -> 'properties' ->> 'monitoring_location_name' as station_name,
    payload -> 'properties' ->> 'state_name' as state_name,
    (payload -> 'geometry' -> 'coordinates' ->> 0)::numeric as longitude,
    (payload -> 'geometry' -> 'coordinates' ->> 1)::numeric as latitude,
    extracted_at,
    load_batch_id
from {{ source('raw', 'stations') }}
