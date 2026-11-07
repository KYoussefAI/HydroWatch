with baseline as (
    select
        observation_key,
        station_key,
        parameter_key,
        date_key,
        observed_at,
        measurement_value,
        count(measurement_value) over previous_readings as baseline_count,
        avg(measurement_value) over previous_readings as baseline_avg,
        stddev_samp(measurement_value) over previous_readings as baseline_stddev
    from {{ ref('fact_water_observation') }}
    window previous_readings as (
        partition by station_key, parameter_key
        order by observed_at
        rows between 20 preceding and 1 preceding
    )
)

select
    b.observation_key,
    s.station_id,
    s.station_name,
    p.parameter_code,
    p.parameter_name,
    p.unit_of_measure,
    b.observed_at,
    b.measurement_value,
    b.baseline_count,
    b.baseline_avg,
    b.baseline_stddev
from baseline b
join {{ ref('dim_station') }} s on b.station_key = s.station_key
join {{ ref('dim_parameter') }} p on b.parameter_key = p.parameter_key
where b.baseline_count >= 8
  and b.baseline_stddev > 0
  and abs(b.measurement_value - b.baseline_avg) > 3 * b.baseline_stddev
