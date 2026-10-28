select 
source_id as parameter_code,
payload -> 'properties' ->> 'parameter_name' as parameter_name,
payload -> 'properties' ->> 'unit_of_measure' as unit_of_measure,
payload -> 'properties' ->> 'parameter_description' as parameter_description,
extracted_at,
load_batch_id
from {{source('raw','parameters')}}