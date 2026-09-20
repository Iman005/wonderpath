import { apiClient } from "@/services/apiClient";
import type { City, FeaturedPlace, Place, PlaceDetail, PlaceKind } from "@/shared/types";

function tripQuery(tripId?: string, dayNumber?: number): string {
  const params = new URLSearchParams();
  if (tripId) params.set("trip_id", tripId);
  if (dayNumber != null) params.set("day_number", String(dayNumber));
  const query = params.toString();
  return query ? `&${query}` : "";
}

export const destinationService = {
  searchCities: (query: string, tripId?: string, dayNumber?: number) =>
    apiClient.get<City[]>(`/cities?q=${encodeURIComponent(query)}${tripQuery(tripId, dayNumber)}`),
  listPlacesForCity: (cityId: string, tripId?: string, kind?: PlaceKind, dayNumber?: number) => {
    const params = new URLSearchParams();
    if (tripId) params.set("trip_id", tripId);
    if (kind) params.set("kind", kind);
    if (dayNumber != null) params.set("day_number", String(dayNumber));
    const query = params.toString();
    return apiClient.get<Place[]>(`/cities/${cityId}/places${query ? `?${query}` : ""}`);
  },
  getPlace: (placeId: string) => apiClient.get<PlaceDetail>(`/places/${placeId}`),
  getCity: (cityId: string) => apiClient.get<City>(`/cities/${cityId}`),
  listFeatured: () => apiClient.get<FeaturedPlace[]>("/places/featured"),
};
