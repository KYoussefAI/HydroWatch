SELECT
    source_id,
    monitoring_location_id,
    parameter_code,
    observation_time::timestamptz AS observed_at,
    value::numeric AS measurement_value,
    extracted_at,
    load_batch_id
FROM {{ source('raw', 'observations') }}