export const GOOGLE_AUTH_MESSAGE = "wanderpath-google";
export const GOOGLE_ID_TOKEN_KEY = "wp_google_id_token";
export const GOOGLE_NONCE_KEY = "wp_google_nonce";
/** Same-origin signal for when popup loses window.opener (Google COOP). */
export const GOOGLE_RESULT_STORAGE_KEY = "wp_google_auth_result";

export function googleCallbackPath() {
  return "/login/google/callback";
}

export function googleRedirectUri() {
  return `${window.location.origin}${googleCallbackPath()}`;
}

export function buildGoogleAuthUrl(clientId: string) {
  const nonce = crypto.randomUUID();
  sessionStorage.setItem(GOOGLE_NONCE_KEY, nonce);
  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: googleRedirectUri(),
    response_type: "id_token",
    response_mode: "fragment",
    scope: "openid email profile",
    nonce,
    prompt: "select_account",
  });
  return `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
}

export function readGoogleHash(hash: string) {
  const params = new URLSearchParams(hash.startsWith("#") ? hash.slice(1) : hash);
  return {
    idToken: params.get("id_token"),
    error: params.get("error"),
  };
}

export type GoogleAuthResult = {
  source: typeof GOOGLE_AUTH_MESSAGE;
  id_token?: string | null;
  error?: string | null;
};

/** Notify the opener login tab even when window.opener is null after Google. */
export function publishGoogleAuthResult(result: GoogleAuthResult) {
  const payload = JSON.stringify({
    ...result,
    ts: Date.now(),
  });
  try {
    sessionStorage.setItem(GOOGLE_ID_TOKEN_KEY, result.error ? `error:${result.error}` : result.id_token || "");
  } catch {
    /* ignore */
  }
  try {
    localStorage.setItem(GOOGLE_RESULT_STORAGE_KEY, payload);
  } catch {
    /* ignore */
  }
  try {
    const channel = new BroadcastChannel(GOOGLE_AUTH_MESSAGE);
    channel.postMessage(result);
    channel.close();
  } catch {
    /* ignore */
  }
  if (window.opener && !window.opener.closed) {
    try {
      window.opener.postMessage(result, window.location.origin);
    } catch {
      /* ignore */
    }
  }
}

export function consumeGoogleAuthStorage(): GoogleAuthResult | null {
  try {
    const raw = localStorage.getItem(GOOGLE_RESULT_STORAGE_KEY);
    if (raw) {
      localStorage.removeItem(GOOGLE_RESULT_STORAGE_KEY);
      const parsed = JSON.parse(raw) as GoogleAuthResult & { ts?: number };
      if (parsed?.source === GOOGLE_AUTH_MESSAGE) return parsed;
    }
  } catch {
    /* ignore */
  }
  try {
    const stored = sessionStorage.getItem(GOOGLE_ID_TOKEN_KEY);
    if (!stored) return null;
    sessionStorage.removeItem(GOOGLE_ID_TOKEN_KEY);
    if (stored.startsWith("error:")) {
      return { source: GOOGLE_AUTH_MESSAGE, error: stored.slice("error:".length) };
    }
    return { source: GOOGLE_AUTH_MESSAGE, id_token: stored };
  } catch {
    return null;
  }
}
