select
    f.station_key,
    f.parameter_key,
    f.date_key,
    s.station_id,
    s.station_name,
    p.parameter_code,
    p.parameter_name,
    p.unit_of_measure,
    d.calendar_date,
    count(*) as observation_count,
    min(f.measurement_value) as min_value,
    max(f.measurement_value) as max_value,
    avg(f.measurement_value) as avg_value
from {{ ref('fact_water_observation') }} f
join {{ ref('dim_station') }} s on f.station_key = s.station_key
join {{ ref('dim_parameter') }} p on f.parameter_key = p.parameter_key
join {{ ref('dim_date') }} d on f.date_key = d.date_key
group by
    f.station_key,
    f.parameter_key,
    f.date_key,
    s.station_id,
    s.station_name,
    p.parameter_code,
    p.parameter_name,
    p.unit_of_measure,
    d.calendar_date
