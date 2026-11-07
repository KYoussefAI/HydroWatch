select
    station_key,
    parameter_key,
    date_key,
    count(*) as duplicate_count
from {{ ref('mart_station_daily') }}
group by station_key, parameter_key, date_key
having count(*) > 1
