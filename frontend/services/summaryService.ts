import { apiClient } from "@/services/apiClient";
import type { TripSummary } from "@/shared/types";

export const summaryService = {
  getTripSummary: (tripId: string) => apiClient.get<TripSummary>(`/trips/${tripId}/summary`),
};
