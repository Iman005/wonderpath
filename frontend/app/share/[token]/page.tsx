"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import fa from "@/i18n/fa";
import { shareService } from "@/services/shareService";
import { ApiError } from "@/services/apiClient";
import type { SharedTrip } from "@/shared/types";
import SharedTripView from "@/components/SharedTripView";
import ErrorNotice from "@/components/ErrorNotice";

export default function PublicSharePage() {
  const params = useParams<{ token: string }>();
  const token = params.token;
  const [snapshot, setSnapshot] = useState<SharedTrip | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setSnapshot(await shareService.getSharedTrip(token));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  return (
    <section className="section">
      <div className="container">
        {loading && <p className="muted">{fa.common.loading}</p>}
        {error && <ErrorNotice message={error} onRetry={load} />}
        {snapshot && <SharedTripView snapshot={snapshot} readOnly />}
      </div>
    </section>
  );
}
