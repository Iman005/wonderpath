import { apiClient } from "@/services/apiClient";
import type { Trip, TripDay, TripPlace } from "@/shared/types";

export interface CreateTripInput {
  name: string;
  start_date: string;
  end_date?: string;
  origin_latitude?: number | null;
  origin_longitude?: number | null;
  origin_label?: string | null;
  budget_cap?: number | null;
  traveler_count?: number;
}

export interface TripUpdatePayload {
  name?: string;
  start_date?: string;
  end_date?: string;
  origin_latitude?: number | null;
  origin_longitude?: number | null;
  origin_label?: string | null;
  budget_cap?: number | null;
  traveler_count?: number;
}

export function tripUpdatePayload(trip: Trip, patch: TripUpdatePayload): TripUpdatePayload {
  return {
    origin_latitude: trip.origin_latitude,
    origin_longitude: trip.origin_longitude,
    origin_label: trip.origin_label,
    budget_cap: trip.budget_cap,
    traveler_count: trip.traveler_count ?? 1,
    ...patch,
  };
}

export const tripService = {
  createTrip: (payload: CreateTripInput) => apiClient.post<Trip>("/trips", payload),
  getTrip: (tripId: string) => apiClient.get<Trip>(`/trips/${tripId}`),
  updateTrip: (tripId: string, payload: TripUpdatePayload) =>
    apiClient.put<Trip>(`/trips/${tripId}`, payload),
  deleteTrip: (tripId: string) => apiClient.del<void>(`/trips/${tripId}`),

  addDay: (tripId: string, dayNumber: number) =>
    apiClient.post<TripDay>(`/trips/${tripId}/days`, { day_number: dayNumber }),

  addDaysBulk: (tripId: string, count: number) =>
    apiClient.post<TripDay[]>(`/trips/${tripId}/days/bulk`, { count }),

  removeLastDay: (tripId: string) => apiClient.del<void>(`/trips/${tripId}/days/last`),

  removeDay: (tripId: string, dayId: string) => apiClient.del<void>(`/trips/${tripId}/days/${dayId}`),

  addPlaceToDay: (
    tripDayId: string,
    placeId: string,
    opts?: {
      note?: string;
      allowDuplicate?: boolean;
      customEntranceFee?: number | null;
      partySize?: number;
    },
  ) =>
    apiClient.post<TripPlace>(`/trip-days/${tripDayId}/places`, {
      place_id: placeId,
      note: opts?.note ?? null,
      allow_duplicate: opts?.allowDuplicate ?? false,
      custom_entrance_fee: opts?.customEntranceFee ?? null,
      party_size: opts?.partySize ?? 1,
    }),

  reorderPlaces: (tripDayId: string, orderedTripPlaceIds: string[]) =>
    apiClient.put<TripPlace[]>(`/trip-days/${tripDayId}/places/reorder`, {
      ordered_trip_place_ids: orderedTripPlaceIds,
    }),

  reorderItinerary: (tripDayId: string, items: { kind: "place" | "stay"; id: string }[]) =>
    apiClient.put<void>(`/trip-days/${tripDayId}/itinerary`, { items }),

  removePlace: (tripDayId: string, placeId: string) =>
    apiClient.del<void>(`/trip-days/${tripDayId}/places/${placeId}`),

  removeStop: (tripDayId: string, tripPlaceId: string) =>
    apiClient.del<void>(`/trip-days/${tripDayId}/stops/${tripPlaceId}`),

  updatePlaceFee: (tripDayId: string, placeId: string, customEntranceFee: number | null) =>
    apiClient.put<TripPlace>(`/trip-days/${tripDayId}/places/${placeId}`, {
      custom_entrance_fee: customEntranceFee,
    }),
};
