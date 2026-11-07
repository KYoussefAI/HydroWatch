{% snapshot snap_stations %}

{{
    config(
        target_schema='history',
        unique_key='station_id',
        strategy='check',
        check_cols=['station_name', 'state_name', 'longitude', 'latitude']
    )
}}

select
    station_id,
    station_key,
    station_name,
    state_name,
    longitude,
    latitude
from {{ ref('dim_station') }}

{% endsnapshot %}
