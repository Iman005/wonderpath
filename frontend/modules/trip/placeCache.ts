"use client";

// The Trip module's API returns TripPlace rows keyed by place_id only
// (see backend TripPlaceOut) — it does not duplicate place details,
// keeping that module decoupled from Destination data. The frontend
// caches full Place objects locally, keyed by id, whenever they're
// fetched from /cities/{id}/places, so the trip editor can render names
// without an extra round trip. The authoritative, always-fresh view is
// still the read-only /summary endpoint (see app/trip/[id]/summary).

import type { Place } from "@/shared/types";

const STORAGE_KEY = "wanderpath_place_cache";

function readCache(): Record<string, Place> {
  if (typeof window === "undefined") return {};
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Record<string, Place>) : {};
  } catch {
    return {};
  }
}

export function cachePlaces(places: Place[]): void {
  if (typeof window === "undefined") return;
  const cache = readCache();
  for (const place of places) {
    cache[place.id] = place;
  }
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(cache));
}

export function getCachedPlace(placeId: string): Place | undefined {
  return readCache()[placeId];
}
