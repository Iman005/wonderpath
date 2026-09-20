"use client";

// Generates (once) and persists the anonymous Device ID used for
// ownerless trip ownership, per architecture spec §2.1. Stored in
// localStorage; sent on every API request via the X-Device-Id header
// (see services/apiClient.ts). This is the ONLY place that mints a new
// id — everything else just reads it.

const STORAGE_KEY = "wanderpath_device_id";

export function getOrCreateDeviceId(): string {
  if (typeof window === "undefined") {
    // Server-side render pass — no localStorage available. Callers on
    // the client will get the real value on mount/hydration.
    return "";
  }

  const existing = window.localStorage.getItem(STORAGE_KEY);
  if (existing) {
    return existing;
  }

  const fresh = crypto.randomUUID();
  window.localStorage.setItem(STORAGE_KEY, fresh);
  return fresh;
}
