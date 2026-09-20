"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import type { Trip } from "@/shared/types";
import { formatIsoDate, formatJalaliSlash, toPersianDigits } from "@/shared/format";
import fa from "@/i18n/fa";

export default function TripCard({
  trip,
  onDeleted,
}: {
  trip: Trip;
  onDeleted: (tripId: string) => Promise<void>;
}) {
  const router = useRouter();
  const [confirming, setConfirming] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const dayCount = trip.days.length;
  const stopCount = trip.days.reduce((sum, d) => sum + d.trip_places.length, 0);

  function goToTrip() {
    router.push(`/trip/${trip.id}`);
  }

  async function handleConfirmDelete() {
    setDeleting(true);
    try {
      await onDeleted(trip.id);
    } finally {
      setDeleting(false);
      setConfirming(false);
    }
  }

  if (confirming) {
    return (
      <div className="trip-card trip-card-confirm">
        <p className="trip-card-name">{fa.trip.confirmDeleteInline}</p>
        <p className="trip-card-meta">{trip.name}</p>
        <div className="row" style={{ marginTop: 12 }}>
          <button className="btn btn-danger-outline btn-sm" onClick={handleConfirmDelete} disabled={deleting}>
            {deleting ? fa.common.loading : fa.trip.confirmDelete}
          </button>
          <button className="btn btn-outline btn-sm" onClick={() => setConfirming(false)} disabled={deleting}>
            {fa.trip.cancel}
          </button>
        </div>
      </div>
    );
  }

  return (
    <article className="trip-card" onClick={goToTrip} onKeyDown={(e) => e.key === "Enter" && goToTrip()} role="link" tabIndex={0}>
      <div className="trip-card-actions">
        <button
          type="button"
          className="icon-btn"
          aria-label={fa.trip.editTrip}
          onClick={(e) => {
            e.stopPropagation();
            goToTrip();
          }}
        >
          ✎
        </button>
        <button
          type="button"
          className="icon-btn danger"
          aria-label={fa.trip.deleteTrip}
          onClick={(e) => {
            e.stopPropagation();
            setConfirming(true);
          }}
        >
          ⌫
        </button>
      </div>
      <p className="trip-card-name">{trip.name}</p>
      <p className="trip-card-meta">
        {toPersianDigits(dayCount)} روز · {toPersianDigits(stopCount)} توقف
        {trip.start_date && trip.end_date
          ? ` · ${fa.home.tripCardRange
              .replace("{start}", formatJalaliSlash(trip.start_date))
              .replace("{end}", formatJalaliSlash(trip.end_date))}`
          : trip.start_date
            ? ` · ${fa.home.tripCardStartsOn}: ${formatIsoDate(trip.start_date)}`
            : ""}
      </p>
    </article>
  );
}
