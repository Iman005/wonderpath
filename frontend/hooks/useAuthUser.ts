import type { AuthUser } from "@/services/authService";

const USER_KEY = "wanderpath_auth_user";

export function getStoredUser(): AuthUser | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
}

export function setStoredUser(user: AuthUser): void {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearStoredUser(): void {
  localStorage.removeItem(USER_KEY);
}

export function displayNameOf(user: AuthUser | null): string {
  if (!user) return "";
  return (user.display_name || user.email || "مسافر").trim();
}

export function initialOf(user: AuthUser | null): string {
  const name = displayNameOf(user);
  return name ? name.charAt(0) : "؟";
}
