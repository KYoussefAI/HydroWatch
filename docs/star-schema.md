# Star schema

```text
                    dim_station
                   (station_key)
                         |
 dim_date --- fact_water_observation --- dim_parameter
 (date_key)         |                 (parameter_key)
                    |
            measurement_value
               observed_at
```

| Relation | Grain | Key |
|---|---|---|
| dim_station | Latest metadata for each station | station_key, station_id |
| dim_parameter | Latest metadata for each code | parameter_key, parameter_code |
| dim_date | One UTC calendar date | date_key |
| fact_water_observation | Station × parameter × event timestamp | observation_key |
| mart_station_daily | Station × parameter × UTC calendar date | station_key + parameter_key + date_key |
| mart_observation_anomalies | One flagged fact observation | observation_key |

The fact keeps both surrogate foreign keys and natural identifiers for
traceability. The model does not equate a RAW duplicate with a new
business event. The business key must be revisited if a station has multiple
simultaneous time series for the same parameter.
