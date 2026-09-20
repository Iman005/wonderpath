"use client";

import { getCachedPlace } from "@/modules/trip/placeCache";
import type { Trip, TripDay } from "@/shared/types";

const STORAGE_KEY = "wanderpath_day_cities";

type Store = Record<string, string | null>;

function dayKey(tripId: string, dayId: string): string {
  return `${tripId}:${dayId}`;
}

function readStore(): Store {
  if (typeof window === "undefined") return {};
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Store) : {};
  } catch {
    return {};
  }
}

function writeStore(store: Store): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
}

export function rememberDayCity(tripId: string, dayId: string, cityId: string | null): void {
  const store = readStore();
  store[dayKey(tripId, dayId)] = cityId;
  writeStore(store);
}

/** `undefined` = never chosen; `null` = explicitly cleared; otherwise the city id. */
export function rememberedCityForDay(tripId: string, dayId: string): string | null | undefined {
  const store = readStore();
  const key = dayKey(tripId, dayId);
  if (!(key in store)) return undefined;
  return store[key];
}

export function inferCityFromDayPlaces(day: TripDay, stays: Trip["stays"] = []): string | undefined {
  const ordered = [...day.trip_places].sort((a, b) => a.order_index - b.order_index);
  for (const stop of ordered) {
    const cityId = stop.city_id || getCachedPlace(stop.place_id)?.city_id;
    if (cityId) return cityId;
  }
  const dayNumber = day.day_number;
  for (const stay of stays) {
    const start = stay.check_in_day_number;
    const nights = stay.nights || 1;
    if (start <= dayNumber && dayNumber < start + nights) {
      const cityId = stay.city_id || getCachedPlace(stay.place_id)?.city_id;
      if (cityId) return cityId;
    }
  }
  return undefined;
}

export function resolvePlannerCityId(trip: Trip, day: TripDay, urlCityId?: string): string | undefined {
  if (urlCityId) return urlCityId;
  const storedThis = rememberedCityForDay(trip.id, day.id);
  if (storedThis === null) return undefined;
  if (storedThis) return storedThis;
  const fromThisDay = inferCityFromDayPlaces(day, trip.stays ?? []);
  if (fromThisDay) return fromThisDay;
  if (day.trip_places.length > 0) return undefined;
  const previous = [...trip.days].find((item) => item.day_number === day.day_number - 1);
  if (!previous) return undefined;
  const storedPrev = rememberedCityForDay(trip.id, previous.id);
  if (storedPrev) return storedPrev;
  return inferCityFromDayPlaces(previous, trip.stays ?? []);
}
