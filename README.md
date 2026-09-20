# WanderPath

Trip planner & local guide for domestic travel inside Iran (Tehran →
Shiraz, Mashhad → Yazd, and so on) — anonymous, device-based ownership,
full RTL/Persian UI, no login, no booking, no AI assistant. Built as a
production-shaped MVP from `docs/architecture-spec.md`.

## Structure

```
backend/     FastAPI + SQLAlchemy + PostgreSQL(/SQLite for dev)
frontend/    Next.js (App Router), RTL, Persian
docs/        The architecture specification this was built from
```

## Running it locally

**1. Backend** (see `backend/README.md` for details):

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/seed_data.py   # sample Iranian cities/places, no API key needed
uvicorn app.main:app --reload --port 8000
```

**2. Frontend** (see `frontend/README.md` for details):

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Then open http://localhost:3000 — create a trip, search "شیراز" or
"تهران", add stops to your days, and check the summary/budget pages.

## What's implemented

Everything in the spec's MVP scope: destination search with a
PostgreSQL-backed cache in front of the Neshan place-data API
(`IPlaceDataProvider`), map rendering as a separate concern
(`IMapProvider`), anonymous device-based trip ownership
(`IIdentityResolver`), multi-day itineraries with reorderable stops,
budget estimation, and a read-only trip summary — all behind the exact
API contract in the spec, verified route-for-route.

23 backend tests pass (unit, service-layer with mocked repos/providers,
repository, and Neshan-adapter contract tests). The frontend typechecks
and builds cleanly. Both were smoke-tested together end-to-end: city
search → add stops → summary → budget → map pins, all confirmed working
with real (seeded) Iranian data.

## What's intentionally not here

Per the spec's exclusions: authentication/user profiles, an AI
assistant, booking/payments, reviews/ratings, notifications. The
`IIdentityResolver` and provider interfaces exist specifically so these
can be added later (real auth, Balad/Google Maps, etc.) without
touching unrelated modules — see §14 of the spec.
