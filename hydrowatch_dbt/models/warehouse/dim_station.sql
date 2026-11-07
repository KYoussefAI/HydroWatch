with ranked as (
    select
        *,
        row_number() over (
            partition by station_id
            order by extracted_at desc, raw_id desc
        ) as record_rank
    from {{ ref('stg_stations') }}
)

select
    md5(station_id) as station_key,
    station_id,
    station_name,
    state_name,
    longitude,
    latitude,
    extracted_at as metadata_extracted_at
from ranked
where record_rank = 1
