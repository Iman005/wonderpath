# WanderPath — Backend

FastAPI backend for WanderPath, an Iranian domestic trip planner. See
`/docs` (architecture spec) at the repo root for full design rationale.

## Quick start (local dev, SQLite — no setup needed)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env

# create tables + sample data (Tehran, Shiraz, Isfahan, Mashhad, Yazd)
python scripts/seed_data.py

uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Running tests

```bash
pytest
```

23 tests covering: identity resolver unit tests, budget calculation unit
tests, trip service tests (mocked repositories), repository tests
(in-memory DB), and Neshan provider contract tests (mocked HTTP).

## Switching to PostgreSQL

Set `DATABASE_URL` in `.env`, e.g.:

```
DATABASE_URL=postgresql+psycopg2://wanderpath:changeme@localhost:5432/wanderpath
```

Then run migrations instead of relying on dev auto-create:

```bash
alembic upgrade head
```

## Project layout

```
app/
 ├── core/               config, DB engine/session
 ├── modules/
 │    ├── destination/   city/place search (+ IPlaceDataProvider interface)
 │    ├── trip/          trip/day/place CRUD, ownership enforcement
 │    ├── identity/      IIdentityResolver + DeviceIdentityResolver
 │    ├── budget/        cost estimation
 │    ├── map/           IMapProvider interface + trip map view
 │    └── summary/       read-only itinerary summary
 ├── infrastructure/
 │    ├── providers/     NeshanPlaceDataProvider, NeshanMapProvider
 │    ├── db/             SQLAlchemy models
 │    └── cache/          Place/City cache-refresh policy
 └── shared/              exceptions, response schemas
```

Every module follows Controller → Service → Repository. Business rules
live only in services; repositories only touch the DB; controllers only
handle HTTP.

## Notes on the Neshan integration

No real `NESHAN_API_KEY` is required to run the app — the seed script
populates real Iranian city/place data directly so the MVP is fully
demoable offline. When a key is configured, `NeshanPlaceDataProvider`
takes over on cache-miss/stale exactly as described in the architecture
spec (§2.3): the app never calls Neshan on every request, only to
refresh the PostgreSQL-backed cache.
