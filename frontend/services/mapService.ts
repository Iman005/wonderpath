import { apiClient } from "@/services/apiClient";
import type { MapViewConfig } from "@/shared/types";

export const mapService = {
  getTripMap: (tripId: string, dayNumber?: number) =>
    apiClient.get<MapViewConfig>(
      `/trips/${tripId}/map${dayNumber != null ? `?day_number=${dayNumber}` : ""}`,
    ),
};
