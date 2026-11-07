# Validation checklist

All tests below require a running PostgreSQL database with RAW data.
Do not treat these as passed until executed and inspected locally.

## Rebuild and data quality

1. Start Docker and initialize RAW from `sql/001_create_raw.sql` in a fresh DB.
2. Run the Python ingestion with a known historical date range.
3. In `hydrowatch_dbt/`, run `dbt debug`, `dbt build`, and `dbt snapshot`.
4. Run `dbt source freshness`; check freshness warnings against the chosen
   historical ingestion time and station coverage.
5. Run `dbt docs generate` and inspect the lineage.

## Fact rerun and source revisions

1. Record fact count and distinct `observation_key` count using
   `scripts/verify_incremental.sql`.
2. Run `dbt build` without changing RAW; counts should be identical.
3. Insert a controlled duplicate source observation into RAW with a new batch
   ID and extraction timestamp. Rebuild and verify the fact grain stays unique.
4. Insert a corrected observation at the same station, parameter, event time
   with a newer `last_modified`, plus fresh extraction metadata. Rebuild and
   verify that the winner changes rather than inserting a duplicate.
5. If the correction falls outside the incremental extraction-time lookback,
   run a full refresh and document the difference.

## SCD Type 2 experiment

1. Run `dbt snapshot` once and record current `snap_stations` rows.
2. Insert a new RAW station metadata row for an existing station with a
   changed name and a newer `extracted_at` (do not overwrite the original).
3. Run `dbt build` to rebuild `dim_station`, then `dbt snapshot`.
4. Verify two versions exist for that station: the old version has
   `dbt_valid_to` set and the new version has `dbt_valid_to IS NULL`.
5. Run the snapshot again with no further change. The version count should
   stay unchanged.

## Deliberate test failure

Use a disposable database or back up the RAW data first.

1. Insert one RAW observation with `monitoring_location_id = NULL`
   and otherwise valid fields, including event time and numeric value.
2. Run `dbt test --select stg_observations`; its `not_null` test should fail.
3. Delete only the deliberately inserted row (using its `raw_id`).
4. Re-run the test and verify it passes.

Avoid running a full `dbt build` on deliberately malformed rows: its
materializations may be partially rebuilt before failing tests.

## Known limitations

- No validation history is recorded in the repo until these experiments
  are executed.
- Station coverage and freshness depend on USGS availability.
- Multiple USGS time series sharing the same station/parameter/timestamp
  require a new grain decision before production use.
