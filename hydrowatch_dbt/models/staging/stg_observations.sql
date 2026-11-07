select
    raw_id,
    source_id,
    time_series_id,
    monitoring_location_id,
    parameter_code,
    statistic_id,
    observation_time::timestamptz as observed_at,
    nullif(value, '')::numeric as measurement_value,
    unit_of_measure,
    approval_status,
    qualifier,
    nullif(last_modified, '')::timestamptz as source_modified_at,
    extracted_at,
    load_batch_id
from {{ source('raw', 'observations') }}
