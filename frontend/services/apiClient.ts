"use client";

import { getAccessToken } from "@/hooks/useAccessToken";
import { getOrCreateDeviceId } from "@/hooks/useDeviceId";
import type { ApiErrorBody } from "@/shared/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  body: ApiErrorBody | null;

  constructor(status: number, body: ApiErrorBody | null, fallbackMessage: string) {
    super(body?.message || fallbackMessage);
    this.status = status;
    this.body = body;
  }
}

interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: unknown;
  /** Attach Authorization bearer when a session token exists (default true). */
  withAuth?: boolean;
  /** Attach X-Device-Id when no bearer token is present (guest fallback). */
  withDeviceId?: boolean;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, withAuth = true, withDeviceId = true } = options;

  const headers: Record<string, string> = { "Content-Type": "application/json" };

  const accessToken = withAuth ? getAccessToken() : null;
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  } else if (withDeviceId) {
    headers["X-Device-Id"] = getOrCreateDeviceId();
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  let parsed: unknown = null;
  try {
    parsed = await response.json();
  } catch {
    // No JSON body — leave null.
  }

  if (!response.ok) {
    throw new ApiError(response.status, parsed as ApiErrorBody, "درخواست با خطا مواجه شد.");
  }

  return parsed as T;
}

export const apiClient = {
  get: <T>(path: string, options?: Omit<RequestOptions, "method" | "body">) =>
    request<T>(path, { ...options, method: "GET" }),
  post: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, "method" | "body">) =>
    request<T>(path, { ...options, method: "POST", body }),
  put: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, "method" | "body">) =>
    request<T>(path, { ...options, method: "PUT", body }),
  del: <T>(path: string, options?: Omit<RequestOptions, "method" | "body">) =>
    request<T>(path, { ...options, method: "DELETE" }),
  upload: async <T>(path: string, formData: FormData): Promise<T> => {
    const headers: Record<string, string> = {};
    const accessToken = getAccessToken();
    if (accessToken) {
      headers.Authorization = `Bearer ${accessToken}`;
    } else {
      headers["X-Device-Id"] = getOrCreateDeviceId();
    }
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers,
      body: formData,
    });
    let parsed: unknown = null;
    try {
      parsed = await response.json();
    } catch {
      // empty
    }
    if (!response.ok) {
      throw new ApiError(response.status, parsed as ApiErrorBody, "درخواست با خطا مواجه شد.");
    }
    return parsed as T;
  },
};
