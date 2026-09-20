import { apiClient } from "@/services/apiClient";
import type { TripStay } from "@/shared/types";

export interface StayCreateInput {
  place_id: string;
  check_in_day_number: number;
  nights: number;
  nightly_rate?: number | null;
  guest_count?: number;
  note?: string | null;
}

export interface StayUpdateInput {
  check_in_day_number?: number;
  nights?: number;
  nightly_rate?: number | null;
  guest_count?: number;
  note?: string | null;
}

export const stayService = {
  addStay: (tripId: string, payload: StayCreateInput) =>
    apiClient.post<TripStay>(`/trips/${tripId}/stays`, payload),
  updateStay: (tripId: string, stayId: string, payload: StayUpdateInput) =>
    apiClient.put<TripStay>(`/trips/${tripId}/stays/${stayId}`, payload),
  removeStay: (tripId: string, stayId: string) =>
    apiClient.del<void>(`/trips/${tripId}/stays/${stayId}`),
};
