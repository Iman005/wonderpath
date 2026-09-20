import { apiClient } from "@/services/apiClient";
import type { NoteAttachment, PackingItem, PackingList, TripNote } from "@/shared/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export function noteAttachmentUrl(path: string | null | undefined): string | null {
  if (!path) return null;
  if (path.startsWith("http")) return path;
  return `${API_BASE_URL}${path}`;
}

export const notebookService = {
  listNotes: (tripId: string, tripDayId?: string) =>
    apiClient.get<TripNote[]>(
      `/trips/${tripId}/notes${tripDayId ? `?trip_day_id=${encodeURIComponent(tripDayId)}` : ""}`,
    ),

  createNote: (tripId: string, body: string, tripDayId?: string | null) =>
    apiClient.post<TripNote>(`/trips/${tripId}/notes`, { body, trip_day_id: tripDayId ?? null }),

  updateNote: (tripId: string, noteId: string, body: string) =>
    apiClient.put<TripNote>(`/trips/${tripId}/notes/${noteId}`, { body }),

  deleteNote: (tripId: string, noteId: string) => apiClient.del<void>(`/trips/${tripId}/notes/${noteId}`),

  uploadAttachment: (tripId: string, noteId: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return apiClient.upload<NoteAttachment>(`/trips/${tripId}/notes/${noteId}/attachments`, form);
  },

  deleteAttachment: (tripId: string, noteId: string, attachmentId: string) =>
    apiClient.del<void>(`/trips/${tripId}/notes/${noteId}/attachments/${attachmentId}`),

  listPackingLists: (tripId: string, tripDayId?: string) =>
    apiClient.get<PackingList[]>(
      `/trips/${tripId}/packing-lists${tripDayId ? `?trip_day_id=${encodeURIComponent(tripDayId)}` : ""}`,
    ),

  createPackingList: (
    tripId: string,
    title: string,
    items: { label: string; is_checked?: boolean }[],
    tripDayId?: string | null,
  ) =>
    apiClient.post<PackingList>(`/trips/${tripId}/packing-lists`, {
      title,
      items,
      trip_day_id: tripDayId ?? null,
    }),

  updatePackingList: (
    tripId: string,
    listId: string,
    payload: { title?: string; items?: { label: string; is_checked?: boolean }[] },
  ) => apiClient.put<PackingList>(`/trips/${tripId}/packing-lists/${listId}`, payload),

  deletePackingList: (tripId: string, listId: string) =>
    apiClient.del<void>(`/trips/${tripId}/packing-lists/${listId}`),

  updatePackingItem: (tripId: string, itemId: string, payload: { label?: string; is_checked?: boolean }) =>
    apiClient.put<PackingItem>(`/trips/${tripId}/packing-items/${itemId}`, payload),
};
