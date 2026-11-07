with ranked as (
    select
        *,
        row_number() over (
            partition by monitoring_location_id, parameter_code, observed_at
            order by source_modified_at desc nulls last, extracted_at desc, raw_id desc
        ) as record_rank
    from {{ ref('stg_observations') }}
)

select
    raw_id,
    source_id,
    time_series_id,
    monitoring_location_id,
    parameter_code,
    statistic_id,
    observed_at,
    measurement_value,
    unit_of_measure,
    approval_status,
    qualifier,
    source_modified_at,
    extracted_at,
    load_batch_id
from ranked
where record_rank = 1
