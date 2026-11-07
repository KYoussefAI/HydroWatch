{{
    config(
        materialized='incremental',
        incremental_strategy='delete+insert',
        unique_key='observation_key',
        on_schema_change='fail'
    )
}}

with observations as (
    select
        md5(
            monitoring_location_id || '|' ||
            parameter_code || '|' ||
            to_char(observed_at at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.US')
        ) as observation_key,
        monitoring_location_id as station_id,
        parameter_code,
        observed_at,
        measurement_value,
        unit_of_measure,
        approval_status,
        source_id,
        source_modified_at,
        extracted_at as source_extracted_at,
        load_batch_id
    from {{ ref('int_observations_latest') }}
),

fact_rows as (
    select
        o.observation_key,
        s.station_key,
        p.parameter_key,
        d.date_key,
        o.station_id,
        o.parameter_code,
        o.observed_at,
        o.measurement_value,
        o.unit_of_measure,
        o.approval_status,
        o.source_id,
        o.source_modified_at,
        o.source_extracted_at,
        o.load_batch_id
    from observations o
    left join {{ ref('dim_station') }} s on o.station_id = s.station_id
    left join {{ ref('dim_parameter') }} p on o.parameter_code = p.parameter_code
    left join {{ ref('dim_date') }} d
        on (o.observed_at at time zone 'UTC')::date = d.calendar_date
)

select *
from fact_rows
{% if is_incremental() %}
where source_extracted_at >= (
    select coalesce(
        max(source_extracted_at) - interval '2 days',
        '1900-01-01'::timestamptz
    )
    from {{ this }}
)
{% endif %}
