import { apiClient } from "@/services/apiClient";
import type { DayWeather } from "@/shared/types";

export const weatherService = {
  getDay: (lat: number, lng: number, date: string, label?: string) => {
    const params = new URLSearchParams({
      lat: String(lat),
      lng: String(lng),
      date,
    });
    if (label) params.set("label", label);
    return apiClient.get<DayWeather>(`/weather?${params.toString()}`);
  },
  getTripWeather: (tripId: string) => apiClient.get<DayWeather[]>(`/trips/${tripId}/weather`),
};
