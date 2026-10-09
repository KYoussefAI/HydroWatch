# HydroWatch

HydroWatch is a Data Engineering project that builds an analytical warehouse from USGS river-monitoring data.

## Scope

HydroWatch monitors three river stations and tracks:

- Discharge (`00060`)
- Gage height (`00065`)
- Water temperature (`00010`)

The core observation grain is:

`station × parameter × timestamp`

## Architecture

USGS Water Data API  
→ Python ingestion  
→ PostgreSQL RAW layer  
→ dbt transformations  
→ dimensional warehouse  
→ analytics marts

## Tech Stack

- Python
- PostgreSQL
- Docker
- dbt

## Current Status

Night 1 complete:

- project initialized
- source explored
- observation grain defined
- PostgreSQL running in Docker
- data contract defined