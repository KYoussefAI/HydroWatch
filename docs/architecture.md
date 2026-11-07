# Warehouse layout

USGS Water Data API → Python ingestion → PostgreSQL RAW → dbt staging
→ latest-observation intermediate → warehouse dimensions and incremental fact
→ daily and anomaly marts.

| Layer | Objects | Grain |
|---|---|---|
| RAW | observations, stations, parameters | One source feature per extraction |
| Staging | stg_observations, stg_stations, stg_parameters | One RAW row, typed/extracted |
| Intermediate | int_observations_latest | One station / parameter / event timestamp |
| Dimensions | dim_station, dim_parameter | One current business key |
| Date dimension | dim_date | One UTC calendar day |
| Fact | fact_water_observation | One station / parameter / event timestamp |
| Marts | mart_station_daily | One station / parameter / UTC day |
| Anomalies | mart_observation_anomalies | One flagged observation |
| History | snap_stations | One station version per detected change |

The dimension keys are deterministic MD5 hashes of business identifiers. The date
key is an integer YYYYMMDD in UTC. The fact observation key hashes the station ID,
parameter code, and UTC observation timestamp (microsecond precision).

The grain deliberately excludes `time_series_id` and `statistic_id`, following the
initial project contract for selected continuous measurements. If two series share
the same station, parameter and timestamp, the intermediate model retains only the
most recently modified/extracted record. Inspect those collisions before expanding
the pipeline to additional series.

A regular staging view exposes RAW changes without copying rows. The warehouse
dimensions are rebuilt as tables. The fact uses PostgreSQL incremental
`delete+insert` based on `observation_key`; a two-day extraction-time overlap
allows recent RAW revisions to be reconsidered. A very old corrected observation
may require a full refresh.

By default dbt's custom schema naming makes configured `+schema: warehouse`
appear as `staging_warehouse` when the profile's target schema is `staging`.
The project supplies `generate_schema_name` to use `warehouse`, `marts`, and
`intermediate` directly, while models without a custom schema use `staging`.
