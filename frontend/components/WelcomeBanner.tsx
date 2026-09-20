"use client";

import { useEffect, useState } from "react";
import fa from "@/i18n/fa";
import { authService, type AuthUser } from "@/services/authService";
import { displayNameOf, getStoredUser, setStoredUser } from "@/hooks/useAuthUser";
import { getAccessToken } from "@/hooks/useAccessToken";
import { subscribeAuthChanged } from "@/hooks/authEvents";

export default function WelcomeBanner() {
  const [user, setUser] = useState<AuthUser | null>(() => getStoredUser());

  function hydrate() {
    if (!getAccessToken()) {
      setUser(null);
      return;
    }
    const cached = getStoredUser();
    if (cached) setUser(cached);
    authService
      .getMe()
      .then((me) => {
        setStoredUser(me);
        setUser(me);
      })
      .catch(() => undefined);
  }

  useEffect(() => {
    hydrate();
    return subscribeAuthChanged(hydrate);
  }, []);

  if (!user) return null;

  const name = displayNameOf(user);

  return (
    <div className="welcome-banner">
      <p className="welcome-banner-title">{fa.profile.welcome.replace("{name}", name)}</p>
      <p className="welcome-banner-sub muted">{fa.profile.welcomeHint}</p>
    </div>
  );
}
