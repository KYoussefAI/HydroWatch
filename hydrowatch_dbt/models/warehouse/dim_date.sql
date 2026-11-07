with bounds as (
    select
        min((observed_at at time zone 'UTC')::date) as first_day,
        max((observed_at at time zone 'UTC')::date) as last_day
    from {{ ref('int_observations_latest') }}
),

dates as (
    select series.day::date as calendar_date
    from bounds
    cross join lateral generate_series(
        bounds.first_day,
        bounds.last_day,
        interval '1 day'
    ) as series(day)
)

select
    to_char(calendar_date, 'YYYYMMDD')::integer as date_key,
    calendar_date,
    extract(year from calendar_date)::integer as year_number,
    extract(month from calendar_date)::integer as month_number,
    extract(day from calendar_date)::integer as day_of_month,
    extract(isodow from calendar_date)::integer as iso_weekday,
    extract(isodow from calendar_date) in (6, 7) as is_weekend
from dates
