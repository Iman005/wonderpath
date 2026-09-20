import { apiClient } from "@/services/apiClient";
import { clearAccessToken, setAccessToken } from "@/hooks/useAccessToken";
import { clearStoredUser, setStoredUser } from "@/hooks/useAuthUser";
import { notifyAuthChanged } from "@/hooks/authEvents";

export interface AuthUser {
  id: string;
  email: string | null;
  display_name: string | null;
}

interface AuthTokenResponse {
  access_token: string;
  user: AuthUser;
}

export const authService = {
  loginWithGoogle(payload: { idToken?: string; accessToken?: string }): Promise<AuthTokenResponse> {
    return apiClient.post<AuthTokenResponse>(
      "/auth/google",
      { id_token: payload.idToken, access_token: payload.accessToken },
      { withAuth: false },
    );
  },

  register(email: string, password: string, displayName?: string): Promise<AuthTokenResponse> {
    return apiClient.post<AuthTokenResponse>(
      "/auth/register",
      { email, password, display_name: displayName || null },
      { withAuth: false },
    );
  },

  loginWithPassword(email: string, password: string): Promise<AuthTokenResponse> {
    return apiClient.post<AuthTokenResponse>("/auth/login", { email, password }, { withAuth: false });
  },

  loginDev(): Promise<AuthTokenResponse> {
    return apiClient.post<AuthTokenResponse>("/auth/dev", undefined, { withAuth: false });
  },

  getMe(): Promise<AuthUser> {
    return apiClient.get<AuthUser>("/auth/me");
  },

  persistSession(response: AuthTokenResponse): void {
    setAccessToken(response.access_token);
    setStoredUser(response.user);
    notifyAuthChanged();
  },

  logout(): void {
    clearAccessToken();
    clearStoredUser();
    notifyAuthChanged();
  },
};
