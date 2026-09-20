import { apiClient } from "@/services/apiClient";
import type { ShareLink, SharedTrip } from "@/shared/types";

export const shareService = {
  enableShare: (tripId: string) => apiClient.post<ShareLink>(`/trips/${tripId}/share`, {}),
  getSharedTrip: (token: string) =>
    apiClient.get<SharedTrip>(`/share/${token}`, { withAuth: false, withDeviceId: false }),
};
