# WanderPath — Software Architecture Specification (v3, Merged)

## 1. Project Context

**Project:** WanderPath — Trip Planner & Local Guide

### Goal

Build a clean, modular, maintainable MVP for an Iranian domestic tourism trip planner. The result should resemble a production-ready architecture while remaining an MVP.

### Target Users

Iranian travelers planning trips **inside Iran only** (e.g. Tehran → Shiraz, Mashhad → Yazd, Tabriz → Rasht). This is NOT an international tourism platform.

### MVP Scope

**Included:**
- Destination search (cities + places)
- Multi-day trip itinerary
- Neshan map integration (through abstraction)
- Neshan place-data integration (through a separate abstraction) + local caching
- Anonymous, device-based trip ownership (no login)
- Full RTL / Persian UI
- Budget estimation (daily + total)
- Read-only trip summary

**Excluded:**
- Authentication / Authorization / User Profiles
- AI Assistant / Chatbot / Recommendation Engine
- Booking, Payments
- Reviews, Ratings, Social Features
- Notifications

---

## 2. Key Architecture Decisions

### 2.1 Anonymous Identity (No Auth)

- Each client generates an anonymous **Device ID** (UUID), stored client-side (localStorage/cookie) and sent on every request via an `X-Device-Id` header.
- `Trip.owner_device_id` stores this value. There is **no `User` table**.
- This logic sits behind `IIdentityResolver`, implemented by `DeviceIdentityResolver`, so real authentication can later replace it without touching business logic.
- Known MVP limitation: trips are tied to a single browser/device; clearing storage or switching devices loses access to existing trips. This is expected, not a bug.

### 2.2 Full RTL / Persian UI

- The entire UI is RTL and Persian from the MVP itself — `dir="rtl"` on the app root, a Persian font (e.g. Vazirmatn), RTL-aware component layout (spacing, icons, animation direction).
- Currency and numbers use Iranian formatting (Toman).
- Text flows through a lightweight i18n layer from day one (Persian-only for now) so a second language can be added later cheaply, without over-engineering it.

### 2.3 Map Rendering vs. Place Data — Two Separate Interfaces

- `IMapProvider` — renders the map only (pins, routes, viewport). Implementation: `NeshanMapProvider` → future: `BaladProvider`, `GoogleMapsProvider`, `OpenStreetMapProvider`.
- `IPlaceDataProvider` — fetches city/place data (search, details, entrance fees where available). Implementation: `NeshanPlaceDataProvider`.
- These are deliberately separate because the data source and the map renderer may change independently.
- **Caching rule:** Place/City data fetched from `IPlaceDataProvider` is persisted into PostgreSQL (`City`/`Place` tables) and refreshed periodically — the app never calls the external API directly on every user request. This protects against latency, rate limits, and provider cost/outages.
- `EstimatedEntranceFee` stays nullable; if the provider has no value, the user can edit it manually.
- API key management, rate limiting, retries, and network error handling live entirely in the infrastructure layer — never in domain services.

---

## 3. Technical Specification

### Frontend
- **Next.js** — component-based, scalable, modern React ecosystem, strong DX.

### Backend
- **FastAPI** — high performance, automatic OpenAPI docs, type-safe, clean path toward future AI features.

### Database
- **PostgreSQL** — relational entities (Trip, TripDay, Place, City, Province, Budget).

### ORM
- **SQLAlchemy** + **Alembic** for migrations.

### Map Provider

```
IMapProvider
    ├── NeshanMapProvider (default)
    ├── BaladProvider (future)
    ├── GoogleMapsProvider (future)
    └── OpenStreetMapProvider (future)
```

### Place Data Provider

```
IPlaceDataProvider
    └── NeshanPlaceDataProvider (default, cached into PostgreSQL)
```

### Identity Provider

```
IIdentityResolver
    └── DeviceIdentityResolver (default, anonymous UUID)
```

---

## 4. Architecture Principles

- Modular Design
- SOLID
- Separation of Concerns
- Dependency Injection
- Low Coupling
- High Cohesion
- Interface-first design
- Avoid over-engineering — this is still an MVP

---

## 5. Modules

### Destination Module
Responsibilities: search cities, search places, retrieve tourism data via `IPlaceDataProvider`.
Contains: Controller, Service, Repository, DTOs.

### Trip Module
Responsibilities: create trip, manage trip days, add/reorder/remove places.
Contains: Controller, Service, Repository, DTOs.

### Identity Module *(new)*
Responsibilities: resolve/generate the Device ID, expose current "owner" identity to other modules via `IIdentityResolver`.
Contains: Middleware/dependency (FastAPI dependency injection), no persistence of its own beyond `owner_device_id` on `Trip`.

### Budget Module
Responsibilities: estimated costs, daily totals, trip totals.

### Map Module
Responsibilities: map visualization only, via `IMapProvider`.

### Localization Module *(new, lightweight)*
Responsibilities: Persian text/number/currency formatting, i18n string lookup, RTL layout helpers.

### Summary Module
Responsibilities: read-only itinerary summary.

---

## 6. Entity Relationships

```
Province
   |
   +-- City
          |
          +-- Place
                  |
                  +-- TripPlace
                          |
                          +-- TripDay
                                  |
                                  +-- Trip (owner_device_id)
```

### Place
- Id
- Name
- Description
- Category
- Province
- City
- Latitude
- Longitude
- Image
- EstimatedEntranceFee (nullable)
- OpeningHours
- SourceProviderId *(new — tracks which external provider/record this was cached from, for refresh/reconciliation)*

Curated detail copy (قدمت، چیستی، رویدادهای مهم) is attached at read time for the place-detail payload — it is tourism knowledge, not a separate table.

### Trip
- Id
- Name
- owner_device_id *(new — replaces any user_id)*
- budget_cap *(Toman; set during trip setup. Soft cap: overage warns, it does not block edits.)*
- CreatedAt / UpdatedAt

### TripExpense
- Id
- TripId
- Label (e.g. غذا، حمل‌ونقل)
- Amount (Toman)

`grand_total = estimated_total (place entrance fees) + expenses_total`. If `grand_total > budget_cap`, the API flags `is_over_budget` / `over_budget_amount` so the UI can offer raising the cap or revising places/expenses.

---

## 7. Data Flow

```
User
 ↓
Next.js UI (RTL / Persian)
 ↓
API Client (attaches X-Device-Id header)
 ↓
FastAPI
 ↓
IIdentityResolver → resolves owner_device_id
 ↓
Application Service
 ↓
Repository
 ↓
PostgreSQL
```

For place/city data specifically:

```
Destination Service
 ↓
IPlaceDataProvider (NeshanPlaceDataProvider)
 ↓
[cache hit?] → PostgreSQL (City/Place tables)
 ↓ (cache miss/stale)
Neshan API → persist → return
```

Business logic belongs only to Services.

---

## 8. API Contracts

```
GET    /cities
GET    /cities/{id}/places

POST   /trips                          (owner resolved from X-Device-Id)
GET    /trips/{id}
PUT    /trips/{id}
DELETE /trips/{id}

POST   /trips/{id}/days
POST   /trip-days/{id}/places
PUT    /trip-days/{id}/places/reorder
DELETE /trip-days/{id}/places/{placeId}

GET    /trips/{id}/summary
GET    /trips/{id}/budget
POST   /trips/{id}/budget/expenses
DELETE /trips/{id}/budget/expenses/{expenseId}
```

All endpoints requiring trip ownership validate `owner_device_id` (from `X-Device-Id`) against `Trip.owner_device_id` before returning/mutating data.

---

## 9. Folder Structure

### Backend
```
app/
 ├── core/               (config, DI wiring, app startup)
 ├── modules/
 │    ├── destination/
 │    ├── trip/
 │    ├── identity/       (IIdentityResolver + DeviceIdentityResolver)
 │    ├── budget/
 │    ├── map/            (IMapProvider + NeshanMapProvider)
 │    └── summary/
 ├── infrastructure/
 │    ├── providers/      (NeshanPlaceDataProvider, NeshanMapProvider)
 │    ├── db/             (SQLAlchemy models, Alembic migrations)
 │    └── cache/          (Place/City sync jobs)
 └── shared/
```

### Frontend
```
app/                      (Next.js app router, dir="rtl")
components/
modules/
services/                 (API client, attaches Device ID header)
hooks/
i18n/                     (Persian strings, number/currency formatting)
shared/
```

---

## 10. Error Handling

- Request validation (Pydantic)
- Global exception handler → standard JSON error shape
- Distinct handling for: validation errors, not-found, ownership mismatch (403), external provider failures (map/place API down → graceful fallback, not a 500)

---

## 11. Logging

- INFO — normal request/response flow, cache refresh events
- WARNING — external provider degraded/slow, missing entrance fee data
- ERROR — external provider failure, unhandled exceptions

---

## 12. Configuration

Environment variables:
- Database connection
- Neshan API Key (map + place data)
- Application settings (env, CORS origins, cache TTL for Place/City sync)
- Device ID cookie/header name and TTL

---

## 13. Testing Strategy

- Unit tests — services, budget calculation logic, IIdentityResolver
- Service layer tests — with mocked repositories and mocked providers (`IMapProvider`, `IPlaceDataProvider`)
- Repository tests — against a test database
- Contract tests — for `NeshanPlaceDataProvider` / `NeshanMapProvider` adapters, to isolate breakage to the infrastructure layer

---

## 14. Future Roadmap

- Real Authentication (would replace `DeviceIdentityResolver` with a JWT/OIDC-based `IIdentityResolver` implementation — no other module changes)
- AI Trip Planner / Recommendations
- Hotel Booking
- Weather integration
- Route optimization
- Notifications
- Second language (i18n layer already scaffolded)

---

## 15. Coding Guidelines

- Keep methods small; meaningful names
- Prefer interfaces wherever abstraction is needed
- UI contains no business logic — renders data only
- Repositories only access data
- Services contain business rules
- Avoid duplicated code, no hardcoded values
- Every module evolves independently
- Self-documenting code

---

## 16. Deliverables

- Complete project architecture
- Database schema
- Folder structure
- Entities
- Services
- Repositories
- Interfaces (`IMapProvider`, `IPlaceDataProvider`, `IIdentityResolver`)
- API endpoints
- UI pages (RTL / Persian)
- Reusable components

This specification guides implementation of a production-quality, modular architecture while delivering only an MVP. Implement step by step; verify architecture after each step before proceeding.
