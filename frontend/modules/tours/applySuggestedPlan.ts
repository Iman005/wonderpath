import { destinationService } from "@/services/destinationService";
import { tripService } from "@/services/tripService";
import { cachePlaces } from "@/modules/trip/placeCache";
import type { Place, Trip } from "@/shared/types";
import { getTour, type TourStop } from "@/modules/tours/catalog";

function namesMatch(placeName: string, target: string): boolean {
  return placeName === target || placeName.includes(target) || target.includes(placeName);
}

async function findPlace(stop: TourStop, cache: Map<string, Place[]>): Promise<Place | null> {
  let places = cache.get(stop.city);
  if (!places) {
    const cities = await destinationService.searchCities(stop.city);
    const city = cities.find((item) => item.name === stop.city) ?? cities[0];
    if (!city) return null;
    places = await destinationService.listPlacesForCity(city.id, undefined, "attraction");
    cache.set(stop.city, places);
  }
  return places.find((place) => namesMatch(place.name, stop.placeName)) ?? null;
}

export async function applySuggestedPlan(trip: Trip, planId: string): Promise<void> {
  const tour = getTour(planId);
  if (!tour) return;
  const days = [...trip.days].sort((a, b) => a.day_number - b.day_number);
  if (days.length === 0) return;
  const cache = new Map<string, Place[]>();
  for (const dayPlan of tour.itinerary) {
    const day = days[dayPlan.day - 1] ?? days[days.length - 1];
    for (const stop of dayPlan.stops) {
      try {
        const place = await findPlace(stop, cache);
        if (!place) continue;
        cachePlaces([place]);
        await tripService.addPlaceToDay(day.id, place.id);
      } catch {
        /* skip a missing or duplicate stop and keep filling the rest */
      }
    }
  }
}
