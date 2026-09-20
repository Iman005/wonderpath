"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import fa from "@/i18n/fa";
import { getAccessToken } from "@/hooks/useAccessToken";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      const search = typeof window !== "undefined" ? window.location.search : "";
      const next = `${pathname || "/app"}${search}`;
      router.replace(`/login?next=${encodeURIComponent(next)}`);
      return;
    }
    setReady(true);
  }, [pathname, router]);

  if (!ready) {
    return (
      <section className="section">
        <div className="container">
          <p className="muted">{fa.common.loading}</p>
        </div>
      </section>
    );
  }

  return <>{children}</>;
}
