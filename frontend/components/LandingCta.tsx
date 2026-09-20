"use client";

import Link from "next/link";
import { useSyncExternalStore } from "react";
import fa from "@/i18n/fa";
import { getAccessToken } from "@/hooks/useAccessToken";

function subscribe(onStoreChange: () => void) {
  window.addEventListener("storage", onStoreChange);
  return () => window.removeEventListener("storage", onStoreChange);
}

function getSnapshot() {
  return getAccessToken();
}

function getServerSnapshot() {
  return null;
}

export default function LandingCta({ className = "", planId }: { className?: string; planId?: string }) {
  const token = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
  const appHref = planId ? `/app?plan=${encodeURIComponent(planId)}` : "/app";
  const href = token ? appHref : `/login?next=${encodeURIComponent(appHref)}`;

  return (
    <Link href={href} className={`btn btn-primary landing-cta ${className}`.trim()}>
      {planId ? fa.tours.startWithPlan : fa.landing.cta}
    </Link>
  );
}
