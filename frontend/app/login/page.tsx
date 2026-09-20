"use client";

import { Suspense, useEffect, useRef, useState, type FormEvent } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import fa from "@/i18n/fa";
import { authService } from "@/services/authService";
import { ApiError } from "@/services/apiClient";
import {
  GOOGLE_AUTH_MESSAGE,
  GOOGLE_RESULT_STORAGE_KEY,
  buildGoogleAuthUrl,
  consumeGoogleAuthStorage,
  type GoogleAuthResult,
} from "@/modules/auth/googlePopup";
import {
  forgetRememberedEmail,
  getRememberedEmail,
  getRememberedPassword,
  readPasswordCredentials,
  storePasswordCredentials,
} from "@/modules/auth/rememberedCredentials";

const LOGIN_TIMEOUT_MS = 45_000;

function GoogleMark() {
  return (
    <svg className="login-google-mark" viewBox="0 0 24 24" width="20" height="20" aria-hidden>
      <path
        fill="#4285F4"
        d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.4h6.5c-.3 1.5-1.2 2.8-2.5 3.6v3h4c2.3-2.1 3.5-5.2 3.5-8.7z"
      />
      <path
        fill="#34A853"
        d="M12 24c3.2 0 6-1.1 8-2.9l-4-3c-1.1.8-2.5 1.2-4 1.2-3.1 0-5.7-2.1-6.6-4.9H1.3v3.1C3.3 21.4 7.4 24 12 24z"
      />
      <path
        fill="#FBBC05"
        d="M5.4 14.4c-.2-.7-.4-1.5-.4-2.4s.1-1.7.4-2.4V6.5H1.3C.5 8.2 0 10.1 0 12s.5 3.8 1.3 5.5l4.1-3.1z"
      />
      <path
        fill="#EA4335"
        d="M12 4.8c1.8 0 3.4.6 4.6 1.8l3.5-3.5C18 1.1 15.2 0 12 0 7.4 0 3.3 2.6 1.3 6.5l4.1 3.1C6.3 6.9 8.9 4.8 12 4.8z"
      />
    </svg>
  );
}

function EyeIcon({ open }: { open: boolean }) {
  if (open) {
    return (
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
        <path d="M3 3l18 18" />
        <path d="M10.6 10.6a2 2 0 002.8 2.8" />
        <path d="M9.9 5.1A10.8 10.8 0 0112 5c7 0 10 7 10 7a16.8 16.8 0 01-3.2 4.4" />
        <path d="M6.1 6.1C3.6 7.8 2 12 2 12s3 7 10 7a10.4 10.4 0 003.8-.7" />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
      <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function LoginForm({ googleClientId }: { googleClientId: string }) {
  const searchParams = useSearchParams();
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const timeoutRef = useRef<number | null>(null);
  const googleHandledRef = useRef(false);
  const showGoogle = Boolean(googleClientId);

  const nextPath = searchParams.get("next") || "/app";

  useEffect(() => {
    setEmail(getRememberedEmail());
    setPassword(getRememberedPassword());
    void readPasswordCredentials().then((saved) => {
      if (!saved) return;
      setEmail(saved.email);
      if (saved.password) setPassword(saved.password);
    });
    return () => {
      if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
    };
  }, []);

  function clearLoginTimeout() {
    if (timeoutRef.current) {
      window.clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }

  function armLoginTimeout() {
    clearLoginTimeout();
    timeoutRef.current = window.setTimeout(() => {
      setLoading(false);
      setError(fa.auth.loginTimeout);
    }, LOGIN_TIMEOUT_MS);
  }

  async function finishLogin(session: Awaited<ReturnType<typeof authService.loginDev>>) {
    clearLoginTimeout();
    authService.persistSession(session);
    const target = nextPath.startsWith("/") ? nextPath : "/app";
    // Full navigation so AuthGuard always sees the fresh token.
    window.location.assign(target);
  }

  function applyGoogleResult(result: GoogleAuthResult) {
    if (googleHandledRef.current) return;
    if (result.error) {
      clearLoginTimeout();
      setLoading(false);
      setError(result.error === "access_denied" ? fa.auth.googleCancelled : fa.auth.googleWidgetFailed);
      return;
    }
    if (typeof result.id_token === "string" && result.id_token) {
      googleHandledRef.current = true;
      void completeGoogleLogin({ idToken: result.id_token });
    }
  }

  useEffect(() => {
    function onMessage(event: MessageEvent) {
      if (event.origin !== window.location.origin) return;
      if (event.data?.source !== GOOGLE_AUTH_MESSAGE) return;
      applyGoogleResult(event.data as GoogleAuthResult);
    }

    function onStorage(event: StorageEvent) {
      if (event.key !== GOOGLE_RESULT_STORAGE_KEY || !event.newValue) return;
      const pending = consumeGoogleAuthStorage();
      if (pending) applyGoogleResult(pending);
    }

    let channel: BroadcastChannel | null = null;
    try {
      channel = new BroadcastChannel(GOOGLE_AUTH_MESSAGE);
      channel.onmessage = (event) => {
        if (event.data?.source === GOOGLE_AUTH_MESSAGE) {
          applyGoogleResult(event.data as GoogleAuthResult);
        }
      };
    } catch {
      channel = null;
    }

    window.addEventListener("message", onMessage);
    window.addEventListener("storage", onStorage);

    const pending = consumeGoogleAuthStorage();
    if (pending) applyGoogleResult(pending);

    const poll = window.setInterval(() => {
      const next = consumeGoogleAuthStorage();
      if (next) applyGoogleResult(next);
    }, 400);

    return () => {
      window.removeEventListener("message", onMessage);
      window.removeEventListener("storage", onStorage);
      window.clearInterval(poll);
      channel?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleGoogleClick() {
    if (!googleClientId) return;
    googleHandledRef.current = false;
    const url = buildGoogleAuthUrl(googleClientId);
    setError(null);
    setLoading(true);
    armLoginTimeout();
    const popup = window.open(url, "wanderpath-google", "width=500,height=700,scrollbars=yes");
    if (!popup) {
      clearLoginTimeout();
      setLoading(false);
      setError(fa.auth.googlePopupBlocked);
      window.location.assign(url);
      return;
    }
    popup.focus();
  }

  async function completeGoogleLogin(payload: { idToken?: string; accessToken?: string }) {
    setLoading(true);
    setError(null);
    armLoginTimeout();
    try {
      const session = await authService.loginWithGoogle(payload);
      await finishLogin(session);
    } catch (err) {
      clearLoginTimeout();
      googleHandledRef.current = false;
      setError(err instanceof ApiError ? err.message : fa.auth.loginFailed);
      setLoading(false);
    }
  }

  async function handlePasswordSubmit(event: FormEvent) {
    event.preventDefault();
    const cleanedEmail = email.trim();
    const cleanedPassword = password;
    if (!cleanedEmail || !cleanedPassword) {
      setError(fa.auth.loginFailed);
      return;
    }
    setLoading(true);
    setError(null);
    armLoginTimeout();
    try {
      const session =
        mode === "signup"
          ? await authService.register(cleanedEmail, cleanedPassword, displayName)
          : await authService.loginWithPassword(cleanedEmail, cleanedPassword);
      if (remember) {
        await storePasswordCredentials(cleanedEmail, cleanedPassword, displayName);
      } else {
        forgetRememberedEmail();
      }
      await finishLogin(session);
    } catch (err) {
      clearLoginTimeout();
      setError(err instanceof ApiError ? err.message : mode === "signup" ? fa.auth.signupFailed : fa.auth.loginFailed);
      setLoading(false);
    }
  }

  async function handleDevLogin() {
    setLoading(true);
    setError(null);
    armLoginTimeout();
    try {
      const session = await authService.loginDev();
      await finishLogin(session);
    } catch (err) {
      clearLoginTimeout();
      setError(err instanceof ApiError ? err.message : fa.auth.devLoginFailed);
      setLoading(false);
    }
  }

  return (
    <section className="login-section">
      <div className="login-wrap">
        <Link href="/" className="nav-text-btn">
          ← {fa.auth.backToLanding}
        </Link>
        <div className="login-card">
        <p className="login-brand">{fa.appName}</p>
        <h1 className="login-title">{mode === "signup" ? fa.auth.signupTitle : fa.auth.loginTitle}</h1>
        <p className="login-subtitle">{mode === "signup" ? fa.auth.signupSubtitle : fa.auth.loginSubtitle}</p>

        <button
          type="button"
          className="login-google-face"
          disabled={!showGoogle || loading}
          onClick={handleGoogleClick}
        >
          <GoogleMark />
          <span>{fa.auth.continueGoogle}</span>
        </button>

        {!showGoogle && <p className="login-hint">{fa.auth.missingClientIdHint}</p>}

        <p className="login-or">
          <span>{fa.auth.orDivider}</span>
        </p>

        <form className="login-form" name="wanderpath-login" onSubmit={handlePasswordSubmit} autoComplete="on">
          {mode === "signup" && (
            <label>
              {fa.auth.nameLabel}
              <input
                className="input input-light"
                name="name"
                value={displayName}
                onChange={(event) => setDisplayName(event.target.value)}
                placeholder={fa.auth.namePlaceholder}
                autoComplete="name"
              />
            </label>
          )}
          <label>
            {fa.auth.emailLabel}
            <input
              id="login-email"
              className="input input-light"
              type="email"
              name="username"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder={fa.auth.emailPlaceholder}
              autoComplete="username"
            />
          </label>
          <label>
            {fa.auth.passwordLabel}
            <span className="password-field">
              <input
                id="login-password"
                className="input input-light"
                type={showPassword ? "text" : "password"}
                name="password"
                required
                minLength={8}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder={fa.auth.passwordPlaceholder}
                autoComplete={mode === "signup" ? "new-password" : "current-password"}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword((current) => !current)}
                aria-label={showPassword ? fa.auth.hidePassword : fa.auth.showPassword}
                title={showPassword ? fa.auth.hidePassword : fa.auth.showPassword}
              >
                <EyeIcon open={showPassword} />
              </button>
            </span>
          </label>
          <label className="login-remember">
            <input type="checkbox" checked={remember} onChange={(event) => setRemember(event.target.checked)} />
            {fa.auth.rememberCredentials}
          </label>
          <button type="submit" className="btn login-submit" disabled={loading}>
            {loading ? fa.common.loading : mode === "signup" ? fa.auth.submitSignup : fa.auth.submitLogin}
          </button>
        </form>

        <p className="login-switch">
          {mode === "signup" ? fa.auth.haveAccount : fa.auth.noAccount}{" "}
          <button type="button" onClick={() => setMode(mode === "signup" ? "login" : "signup")}>
            {mode === "signup" ? fa.auth.switchToLogin : fa.auth.switchToSignup}
          </button>
        </p>

        <button type="button" className="login-dev" onClick={handleDevLogin} disabled={loading}>
          {fa.auth.devLogin}
        </button>

        {error && <p className="login-error">{error}</p>}
        </div>
      </div>
    </section>
  );
}

export default function LoginPage() {
  const clientId = (process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "").trim();

  return (
    <Suspense fallback={<p className="muted container">{fa.common.loading}</p>}>
      <LoginForm googleClientId={clientId} />
    </Suspense>
  );
}
