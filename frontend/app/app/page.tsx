"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import fa from "@/i18n/fa";
import { tripService } from "@/services/tripService";
import { ApiError } from "@/services/apiClient";
import { getLocalTripIds, addLocalTripId, removeLocalTripId } from "@/modules/trip/localTrips";
import type { Trip } from "@/shared/types";
import TripCard from "@/components/TripCard";
import EmptyState from "@/components/EmptyState";
import JalaliDatePicker from "@/components/JalaliDatePicker";
import WelcomeBanner from "@/components/WelcomeBanner";
import SuggestionBanner from "@/components/SuggestionBanner";
import { addDaysToIso, inclusiveDayCount, toPersianDigits } from "@/shared/format";
import { getTour } from "@/modules/tours/catalog";

function todayIsoDate(): string {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${now.getFullYear()}-${month}-${day}`;
}

function AppHomePageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const planId = searchParams.get("plan");
  const suggestedPlan = planId ? getTour(planId) : undefined;
  const [tripName, setTripName] = useState("");
  const [startDate, setStartDate] = useState(todayIsoDate);
  const [endDate, setEndDate] = useState(todayIsoDate);
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const [trips, setTrips] = useState<Trip[]>([]);
  const [loadingTrips, setLoadingTrips] = useState(true);

  async function loadTrips() {
    setLoadingTrips(true);
    const ids = getLocalTripIds();
    const results = await Promise.all(
      ids.map(async (id) => {
        try {
          return await tripService.getTrip(id);
        } catch {
          return null;
        }
      })
    );
    setTrips(results.filter((t): t is Trip => t !== null));
    setLoadingTrips(false);
  }

  useEffect(() => {
    loadTrips();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!suggestedPlan) return;
    setTripName(suggestedPlan.name);
    const start = todayIsoDate();
    setStartDate(start);
    setEndDate(addDaysToIso(start, suggestedPlan.days - 1));
  }, [suggestedPlan]);

  async function handleCreateTrip(e: React.FormEvent) {
    e.preventDefault();
    const trimmedName = tripName.trim();
    if (!trimmedName) {
      setCreateError(fa.errors.tripNameRequired);
      return;
    }
    const nameTaken = trips.some(
      (trip) => trip.name.trim().toLocaleLowerCase("fa") === trimmedName.toLocaleLowerCase("fa")
    );
    if (nameTaken) {
      setCreateError(fa.errors.tripNameDuplicate);
      return;
    }
    if (!startDate) {
      setCreateError(fa.errors.startDateRequired);
      return;
    }
    if (!endDate) {
      setCreateError(fa.errors.endDateRequired);
      return;
    }
    if (endDate < startDate) {
      setCreateError(fa.errors.endDateBeforeStart);
      return;
    }
    const today = todayIsoDate();
    if (startDate < today) {
      setCreateError(fa.errors.startDateInPast);
      return;
    }
    if (inclusiveDayCount(startDate, endDate) > 30) {
      setCreateError(fa.trip.rangeTooLong);
      return;
    }
    setCreating(true);
    setCreateError(null);
    try {
      const trip = await tripService.createTrip({
        name: trimmedName,
        start_date: `${startDate}T00:00:00`,
        end_date: `${endDate}T00:00:00`,
      });
      addLocalTripId(trip.id);
      const next = suggestedPlan ? `/trip/${trip.id}?plan=${encodeURIComponent(suggestedPlan.id)}` : `/trip/${trip.id}`;
      router.push(next);
    } catch (err) {
      if (err instanceof ApiError) {
        const msg = err.message.toLowerCase();
        if (msg.includes("name")) setCreateError(fa.errors.tripNameDuplicate);
        else if (msg.includes("start date") || msg.includes("before today")) setCreateError(fa.errors.startDateInPast);
        else setCreateError(err.message);
      } else {
        setCreateError(fa.errors.generic);
      }
      setCreating(false);
    }
  }

  async function handleDeleted(tripId: string) {
    await tripService.deleteTrip(tripId);
    removeLocalTripId(tripId);
    setTrips((prev) => prev.filter((trip) => trip.id !== tripId));
  }

  return (
    <section className="home-page">
      <SuggestionBanner variant="backdrop" />
      <div className="container container-wide home-page-front">
        <div className="home-split">
          <div className="home-welcome">
            <WelcomeBanner />
          </div>
          <div className="home-trips-col">
            <h2 className="home-trips-title">{fa.home.myTripsTitle}</h2>
            {loadingTrips ? (
              <p className="muted">{fa.common.loading}</p>
            ) : trips.length === 0 ? (
              <EmptyState message={fa.home.noTripsYet} />
            ) : (
              <div className="trip-grid">
                {trips.map((trip) => (
                  <TripCard key={trip.id} trip={trip} onDeleted={handleDeleted} />
                ))}
              </div>
            )}
          </div>

          <div className="home-create-col">
            <div className="create-panel">
              <h2 className="home-create-title">
                {suggestedPlan ? fa.home.createFromPlan : fa.home.createTrip}
              </h2>
              {suggestedPlan && (
                <p className="muted home-plan-hint">
                  {fa.home.planHint
                    .replace("{name}", suggestedPlan.name)
                    .replace("{n}", toPersianDigits(suggestedPlan.days))
                    .replace("{place}", `${suggestedPlan.province} · ${suggestedPlan.city}`)}
                </p>
              )}
              <form onSubmit={handleCreateTrip}>
                <input
                  className="input"
                  placeholder={fa.home.tripNamePlaceholder}
                  value={tripName}
                  onChange={(e) => setTripName(e.target.value)}
                  readOnly={Boolean(suggestedPlan)}
                  aria-label={fa.home.tripNamePlaceholder}
                />
                <JalaliDatePicker
                  range
                  label={fa.home.dateRangeLabel}
                  value={startDate}
                  endValue={endDate}
                  onRangeChange={(start, end) => {
                    setStartDate(start);
                    setEndDate(end);
                  }}
                  minDate={todayIsoDate()}
                />
                <button className="btn btn-primary" type="submit" disabled={creating}>
                  {creating ? fa.common.loading : fa.home.createTrip}
                </button>
              </form>
              {createError && (
                <p style={{ color: "var(--terracotta)", marginTop: 4, fontWeight: 700 }}>{createError}</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function AppHomePage() {
  return (
    <Suspense
      fallback={
        <section className="section">
          <div className="container">
            <p className="muted">{fa.common.loading}</p>
          </div>
        </section>
      }
    >
      <AppHomePageInner />
    </Suspense>
  );
}
