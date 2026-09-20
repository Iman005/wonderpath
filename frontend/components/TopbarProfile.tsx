"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import fa from "@/i18n/fa";
import { authService, type AuthUser } from "@/services/authService";
import {
  displayNameOf,
  getStoredUser,
  setStoredUser,
} from "@/hooks/useAuthUser";
import { getAccessToken } from "@/hooks/useAccessToken";
import { subscribeAuthChanged } from "@/hooks/authEvents";

export default function TopbarProfile() {
  const router = useRouter();
  // Always start null so SSR and the first client paint match (localStorage
  // is only available after mount — reading it in useState caused hydration errors).
  const [user, setUser] = useState<AuthUser | null>(null);
  const [open, setOpen] = useState(false);
  const wrapRef = useRef<HTMLDivElement | null>(null);

  function hydrate() {
    const token = getAccessToken();
    if (!token) {
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
      .catch(() => {
        // Stale token — clear quietly; AuthGuard handles protected routes.
      });
  }

  useEffect(() => {
    hydrate();
    return subscribeAuthChanged(hydrate);
  }, []);

  useEffect(() => {
    function onDocClick(event: MouseEvent) {
      if (!wrapRef.current?.contains(event.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  if (!user) return null;

  function handleLogout() {
    authService.logout();
    setUser(null);
    setOpen(false);
    router.push("/login");
  }

  const name = displayNameOf(user);

  return (
    <div className="topbar-profile" ref={wrapRef}>
      <button
        type="button"
        className={`topbar-profile-btn${open ? " is-open" : ""}`}
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-haspopup="menu"
      >
        <img src="/user.svg" alt="" className="topbar-avatar" />
        <span className="topbar-profile-name">{name}</span>
        <span className="topbar-profile-caret" aria-hidden>
          ▾
        </span>
      </button>

      {open && (
        <div className="topbar-profile-menu" role="menu">
          <div className="topbar-profile-menu-hero">
            <img src="/user.svg" alt="" className="topbar-avatar topbar-avatar-lg" />
            <p className="topbar-profile-menu-title">{fa.profile.title}</p>
            <p className="topbar-profile-menu-name">{name}</p>
            {user.email && <p className="topbar-profile-menu-email muted">{user.email}</p>}
          </div>
          <button type="button" className="topbar-profile-logout" onClick={handleLogout}>
            {fa.profile.logout}
          </button>
        </div>
      )}
    </div>
  );
}
