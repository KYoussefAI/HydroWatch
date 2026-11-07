select 'observations' as dataset, load_batch_id::text as batch_id, count(*) as rows
from raw.observations
group by load_batch_id
union all
select 'stations', load_batch_id::text, count(*)
from raw.stations
group by load_batch_id
union all
select 'parameters', load_batch_id::text, count(*)
from raw.parameters
group by load_batch_id
order by batch_id, dataset;
