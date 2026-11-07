-- Run against the hydrowatch database before first ingestion.
create schema if not exists raw;

create table if not exists raw.observations (
    raw_id bigserial primary key,
    source_id text,
    time_series_id text,
    monitoring_location_id text,
    parameter_code text,
    statistic_id text,
    observation_time text,
    value text,
    unit_of_measure text,
    approval_status text,
    qualifier text,
    last_modified text,
    method_category text,
    geometry jsonb,
    extracted_at timestamptz not null,
    load_batch_id uuid not null
);

create table if not exists raw.stations (
    raw_id bigserial primary key,
    source_id text not null,
    payload jsonb not null,
    extracted_at timestamptz not null,
    load_batch_id uuid not null
);

create table if not exists raw.parameters (
    raw_id bigserial primary key,
    source_id text not null,
    payload jsonb not null,
    extracted_at timestamptz not null,
    load_batch_id uuid not null
);

create index if not exists idx_raw_observations_station_time
    on raw.observations (monitoring_location_id, observation_time);

create index if not exists idx_raw_observations_batch
    on raw.observations (load_batch_id);

create index if not exists idx_raw_stations_batch
    on raw.stations (load_batch_id);

create index if not exists idx_raw_parameters_batch
    on raw.parameters (load_batch_id);
