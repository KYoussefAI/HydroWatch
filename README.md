# HydroWatch

A local ELT pipeline and analytical warehouse for river-monitoring data from the
USGS Water Data API. The project tracks three stations in Montana and three
parameters: discharge (00060), gage height (00065), and water temperature (00010).

## Pipeline

```text
USGS OGC API
    -> Python ingestion, retries, cursor pagination
    -> PostgreSQL raw tables + archived JSON by batch
    -> dbt staging views
    -> intermediate latest-observation view
    -> dim_station / dim_parameter / dim_date
    -> incremental fact_water_observation
    -> daily summary + rolling outlier marts
```

See [architecture](docs/architecture.md), [data contract](docs/data-contract.md),
and [design decisions](docs/decisions.md).

## Requirements

- Docker Desktop with WSL integration (or another working Docker engine)
- Python virtual environment, with packages from `requirements.txt`
- dbt-postgres (included in `requirements.txt`)
- PostgreSQL exposed on localhost:5433 using the Compose configuration

## Local setup

```bash
cp .env.example .env
# Set a PostgreSQL password in .env, then:
docker compose up -d
pip install -r requirements.txt
```

The dbt profile lives in `~/.dbt/profiles.yml` and is **not** committed.
Use a profile matching the project's `hydrowatch_dbt` name:

```yaml
hydrowatch_dbt:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      port: 5433
      user: hydrowatch_user
      password: "{{ env_var('POSTGRES_PASSWORD') }}"
      dbname: hydrowatch
      schema: staging
      threads: 4
```

dbt does not load `.env` automatically. Export your variable into the shell:

```bash
set -a
source .env
set +a
```

Make the RAW schema in a new database:

```bash
docker exec -i hydrowatch-postgres psql -U hydrowatch_user -d hydrowatch \
  < sql/001_create_raw.sql
```

For an existing database, the DDL uses `IF NOT EXISTS` and preserves rows.
It does not migrate incompatible preexisting column types. In particular,
`raw.parameters.load_batch_id` must be `uuid`.

## Ingest and build

From the repository root:

```bash
python src/ingest/load_raw.py
cd hydrowatch_dbt
dbt debug
dbt build
dbt snapshot
dbt source freshness
dbt docs generate
```

The ingestion uses a rolling last-24-hour UTC window unless `USGS_DATETIME`
is set to an explicit historical range, such as:

```bash
export USGS_DATETIME='2025-10-09T00:00:00Z/2025-10-10T00:00:00Z'
```

The three selected locations are `USGS-06115200`, `USGS-06066500`,
and `USGS-06052500`. Data availability varies; a fresh rolling window can
be empty, even while metadata is available. Source freshness is a separate
signal, not proof that all stations produced recent observations.

`dbt build` creates the views/tables and runs data tests. `dbt snapshot`
creates/updates station history. `dbt docs generate` writes a lineage catalog
to `hydrowatch_dbt/target/`; view it with `dbt docs serve`.

## Replaying a failed ingestion

Source snapshots are saved under `data/raw/{observations,stations,parameters}/`
and ignored by Git. Inspect an existing batch before applying it:

```bash
python src/ingest/replay_raw.py <original-batch-uuid>
python src/ingest/replay_raw.py <original-batch-uuid> --apply
```

Replay loads the archived JSON without contacting USGS, using a **new batch ID**
and a new extraction timestamp. RAW is append-only and replay can create
duplicate source observations; the intermediate model selects one winner per
business grain. Archive files must include the batch UUID and page number.
Don't replay an incomplete extraction unless missing pages are understood.

## Warehouse

The intended observation grain is **station × parameter × UTC event timestamp**.
The intermediate model chooses the most recently modified/extracted row when
RAW contains multiple copies. This assumes the selected USGS time series have
one meaningful measurement per station/parameter/time; check for collisions
before expanding to other series.

The fact uses `delete+insert` with a deterministic `observation_key` and a
two-day extraction-time lookback. Normal reruns should not grow the fact.
For historical corrections outside the lookback, use `dbt build --full-refresh`
after assessing the affected period.

Station metadata history is stored by the `snap_stations` SCD Type 2 snapshot,
with the station ID as the business key and check columns for name, state, and
coordinates. Repeated unchanged metadata does not create a new history version.

Marts:
- `mart_station_daily`: min, max, mean, and count by UTC date/station/parameter.
- `mart_observation_anomalies`: exploratory readings more than three sample
  standard deviations from the preceding 20 readings, with at least eight
  baseline readings. This is not a scientific flood-alert threshold.

## Validation

From `hydrowatch_dbt/`:

```bash
dbt build
dbt test
dbt snapshot
```

From the repository root, the SQL checks can be run with:

```bash
docker exec -i hydrowatch-postgres psql -U hydrowatch_user -d hydrowatch \
  < scripts/verify_batches.sql
docker exec -i hydrowatch-postgres psql -U hydrowatch_user -d hydrowatch \
  < scripts/verify_incremental.sql
```

Record the fact count, rerun `dbt build` without changing RAW, and verify
that both the count and duplicate count remain unchanged. Re-run after ingesting
revised source rows. A practical failure test and SCD2 experiment are described
in [validation notes](docs/validation.md).

## Scope and limits

The source is a small set of selected USGS stations, not a complete national
hydrology dataset. RAW duplicates are retained by design. The deduplication
rule favors recent revisions but can conceal multiple distinct series that share
the declared grain. Staging numeric casts assume the source values are parseable.
The freshness rules use last extraction time, not last observation event time.
The anomaly mart is a statistical heuristic.

The warehouse additions should be validated against a running local PostgreSQL
database after pulling; a successful Git push alone does not execute dbt.
