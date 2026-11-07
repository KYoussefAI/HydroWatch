with ranked as (
    select
        *,
        row_number() over (
            partition by parameter_code
            order by extracted_at desc, raw_id desc
        ) as record_rank
    from {{ ref('stg_parameters') }}
)

select
    md5(parameter_code) as parameter_key,
    parameter_code,
    parameter_name,
    unit_of_measure,
    parameter_description,
    medium
from ranked
where record_rank = 1
