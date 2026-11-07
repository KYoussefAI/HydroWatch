# Design decisions

## Keep RAW append-only

Preserve API payloads as JSON archives and PostgreSQL rows with ingestion
metadata. Repeated ingestion creates RAW duplicates, but those duplicates are
useful for replay and source provenance. Don't add uniqueness constraints at
the RAW layer that discard source revisions.

## Treat staging as a view layer

dbt stages parse timestamps, cast values, and extract JSONB attributes.
Views leave the source untouched and expose new RAW records when queried.

## Separate deduplication from staging

\`int_observations_latest\` deduplicates by station, parameter, and event
timestamp. Revision timestamp takes precedence; extraction timestamp and
\`raw_id\` break ties. This selects one record even when values conflict.
\`time_series_id\` and \`statistic_id\` remain available for future grain audits.

## Use deterministic dimension identifiers

Station and parameter surrogate keys are stable MD5s of their source
identifiers. A numeric date key represents the UTC calendar day. Hashes make
rebuilds repeatable without a shared sequence allocator.

## Incremental fact rather than append

\`delete+insert\` replaces existing rows by observation key instead of
accumulating another copy every time the same source interval is loaded.
The incremental filter uses extraction time (not event time), so a newly
arrived correction to an old observation is eligible. The two-day overlap
assumes a bounded ingestion/reprocessing delay; a full refresh is required
for older corrections outside the lookback.

## Store metadata history separately from current dimensions

\`dim_station\` describes the latest known station metadata. A dbt snapshot
tracks changes by stable station ID, preserving previous attribute versions.
The fact is joined to a stable station key and does not attempt a historical
as-of station-version join. That distinction matters if station locations
or descriptions change over time.

## Do not overstate anomaly detection

The anomaly mart uses a rolling statistical baseline; it is a quick data
exploration aid, not a hydrological alerting or forecasting system.
