# HydroWatch Data Contract

## Source

- Source system: USGS Water Data API
- Dataset: Continuous observations
- Endpoint: `/collections/continuous/items`
- Format: JSON / GeoJSON

---

## Dataset: observations

### Row meaning

One row represents one water measurement recorded at one monitoring station, for one parameter, at one timestamp.

### Grain

One observation is identified at the business level by:

`monitoring_location_id + parameter_code + time`

### Event time

`time`

The timestamp when the measurement was recorded by the source.

### Extraction time

`extracted_at`

The timestamp when HydroWatch retrieved the record from the API.

---

## Fields

| Field | Meaning | Expected raw type | Nullable |
|---|---|---|---|
| time_series_id | Identifier of the USGS time series | text | no |
| monitoring_location_id | Monitoring station identifier | text | no |
| parameter_code | Identifies what is being measured | text | no |
| statistic_id | Statistic represented by the observation | text | no |
| time | Observation/event timestamp | text | no |
| value | Measurement value from the API | text | possible |
| unit_of_measure | Unit associated with the value | text | possible |
| approval_status | Approved or provisional status | text | possible |
| qualifier | Additional source qualifier | text | yes |
| last_modified | Last time USGS refreshed the record | text | possible |
| method_category | Measurement method category | text | yes |
| extracted_at | Time HydroWatch extracted the record | timestamp | no |

---

## Raw-layer policy

The RAW layer preserves source data as closely as practical.

HydroWatch does not perform heavy cleaning, analytical transformation, or business modeling during extraction.

Type conversions and transformations will happen later in the transformation layer.

---

## Uniqueness assumption

For the selected continuous instantaneous series, HydroWatch assumes that one business observation should exist per:

`monitoring_location_id + parameter_code + time`

`time_series_id` and `statistic_id` are preserved from the source so this assumption can be validated during ingestion.

## Duplicate definition

An exact duplicate is the same observation retrieved more than once with the same identifying fields and same measurement data.

If the same station, parameter, and event time appears again with a different value, approval status, or `last_modified`, it may represent a source revision rather than a simple duplicate and should not be blindly discarded.

## Possible bad-data conditions

Examples include:

- missing `monitoring_location_id`, `parameter_code`, or `time`;
- invalid or unparseable timestamps;
- missing or non-numeric measurement values when a numeric value is expected;
- unexpected or missing units;
- exact duplicate records;
- conflicting records for the same expected observation grain.