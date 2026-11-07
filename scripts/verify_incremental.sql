-- Run after an initial dbt build. Repeat after an unchanged dbt build.
select
    count(*) as fact_rows,
    count(distinct observation_key) as distinct_business_keys,
    count(*) - count(distinct observation_key) as duplicates
from warehouse.fact_water_observation;

-- One row per observation grain; this query should return no rows.
select station_id, parameter_code, observed_at, count(*)
from warehouse.fact_water_observation
group by station_id, parameter_code, observed_at
having count(*) > 1;
