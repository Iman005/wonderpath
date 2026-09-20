# WanderPath — Frontend

Next.js (App Router) frontend for WanderPath. Full RTL, Persian UI from
the ground up.

## Quick start

```bash
cd frontend
npm install
cp .env.example .env.local   # point NEXT_PUBLIC_API_BASE_URL at the backend
npm run dev
```

Open http://localhost:3000 (landing). Sign in at `/login` with Google,
then use `/app`. Make sure the backend is running first (see
`../backend/README.md`) and seeded.

## How ownership works (Google sign-in)

On login, the frontend receives a JWT from `POST /auth/google` and
stores it in `localStorage` (`hooks/useAccessToken.ts`). Every API
request sends `Authorization: Bearer …` via `services/apiClient.ts`.
Trip ownership is the authenticated **user id** (still stored in the
`owner_device_id` column on the backend for now).

The legacy `X-Device-Id` header path still works on the backend as a
guest fallback for old clients/tests, but `/app` and `/trip/*` require
login in the frontend (`components/AuthGuard.tsx`).

**Phone/SMS OTP is not implemented yet** — deferred until an Iranian SMS
provider is chosen.

Because the API has no "list my trips" endpoint, the frontend still
tracks which trip ids this browser created in `localStorage`
(`modules/trip/localTrips.ts`).

## Environment

Copy `.env.example` → `.env.local` and set at minimum:

- `NEXT_PUBLIC_API_BASE_URL` — backend URL (default `http://localhost:8000`)
- `NEXT_PUBLIC_GOOGLE_CLIENT_ID` — from [Google Cloud Console](https://console.cloud.google.com/) OAuth client (Web application). Add Authorized JavaScript origins `http://localhost:3000` and Authorized redirect URI `http://localhost:3000/login/google/callback`.

Optional: `NEXT_PUBLIC_NESHAN_API_KEY` for Neshan map tiles. This must be a
Neshan **web** key — a `service.*` key is for the backend APIs and is ignored
here so it never leaks into the browser bundle. Without it the map falls back
to OpenFreeMap tiles.

## Map fonts

Persian map labels require the MapLibre RTL text plugin; without it MapLibre
draws Arabic-script text unshaped and in logical order (detached, reversed
letters). `npm run dev` and `npm run build` vendor it into `public/` via
`scripts/copy-rtl-plugin.mjs`, so it is served from our own origin rather than
a CDN.

## Project layout

```
app/                  Landing (`/`), login, `/app`, `/trip/[id]/*`
components/           UI including AuthGuard, TripRouteMap, search panels
services/             auth, destination, trip, budget, map, summary
hooks/                useAccessToken, useDeviceId (legacy guest)
modules/trip/         local trip-id tracking, place cache
i18n/fa.ts            Persian strings
shared/               types, format helpers, mapStyle, polyline
```

## Design notes

Palette and type are deliberately not the "default AI look": a deep
indigo-dusk band (inspired by desert night skies) frames warm parchment
content surfaces; Persian-tile turquoise is the primary interactive
color; caravanserai-brick terracotta is reserved for money and warnings
only. Vazirmatn (a Persian-native variable sans) carries both display
and body text; **Space Mono is used only for numerals** — prices, stop
counts — as a small nod to bazaar ledger bookkeeping, where figures are
set apart from prose.

The itinerary view's signature element is the "route stitch": a dashed
line threading numbered waypoint markers down each day column. The
numbering is not decorative — it's the actual visit order, which the
person can reorder with the ↑/↓ controls on each stop.

## Building for production

```bash
npm run build
npm run start
```
