SELECT
source_id as station_id,
payload -> 'properties' ->> 'monitoring_location_name' as station_name, -- this is new syntax, explain to me
extracted_at, 
load_batch_id
from {{source('raw','stations')}}db