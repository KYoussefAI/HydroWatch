select
    monitoring_location_id,
    parameter_code,
    observed_at,
    count(*) as duplicate_count
from {{ ref('int_observations_latest') }}
group by monitoring_location_id, parameter_code, observed_at
having count(*) > 1
