"use client";

// The backend's API contract deliberately has no "list my trips"
// endpoint (see spec §8) — trip ownership is anonymous and
// device-scoped, so "my trips" is purely a client-side concern: we
// remember which trip ids this device created, then fetch each one's
// current state from the API. This is consistent with the MVP
// limitation noted in the spec (§2.1): losing localStorage loses access
// to trip history, by design.

const STORAGE_KEY = "wanderpath_trip_ids";

export function getLocalTripIds(): string[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as string[]) : [];
  } catch {
    return [];
  }
}

export function addLocalTripId(tripId: string): void {
  if (typeof window === "undefined") return;
  const ids = getLocalTripIds();
  if (!ids.includes(tripId)) {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify([tripId, ...ids]));
  }
}

export function removeLocalTripId(tripId: string): void {
  if (typeof window === "undefined") return;
  const ids = getLocalTripIds().filter((id) => id !== tripId);
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(ids));
}
