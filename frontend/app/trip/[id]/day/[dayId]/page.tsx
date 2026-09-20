"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import dynamic from "next/dynamic";
import Link from "next/link";
import fa from "@/i18n/fa";
import { tripService } from "@/services/tripService";
import { stayService } from "@/services/stayService";
import { mapService } from "@/services/mapService";
import { weatherService } from "@/services/weatherService";
import { ApiError } from "@/services/apiClient";
import { dayDateIso, formatDayOrdinal, formatDistanceKm, formatDrivingDurationShort, formatJalaliSlash } from "@/shared/format";
import type { City, DayWeather, MapViewConfig, Trip } from "@/shared/types";
import DestinationSearchPanel from "@/components/DestinationSearchPanel";
import DayPlanColumn, { buildDayItinerary, type DayItineraryItem } from "@/components/DayPlanColumn";
import ErrorNotice from "@/components/ErrorNotice";
import AppOverlay from "@/components/AppOverlay";
import WeatherRail from "@/components/WeatherRail";
import { resolvePlannerCityId } from "@/modules/trip/dayCityMemory";

const TripRouteMap = dynamic(() => import("@/components/TripRouteMap"), { ssr: false });

export default function TripDayPlannerPage() {
  const params = useParams<{ id: string; dayId: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();
  const tripId = params.id;
  const dayId = params.dayId;
  const urlCityId = searchParams.get("city") ?? undefined;

  const [trip, setTrip] = useState<Trip | null>(null);
  const [mapConfig, setMapConfig] = useState<MapViewConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [ticket, setTicket] = useState<null | "plan" | "map">(null);
  const [weatherCity, setWeatherCity] = useState<City | null>(null);
  const [weather, setWeather] = useState<DayWeather | null>(null);
  const [weatherLoading, setWeatherLoading] = useState(false);

  async function load(opts?: { silent?: boolean }) {
    if (!opts?.silent) {
      setLoading(true);
      setError(null);
    }
    try {
      const result = await tripService.getTrip(tripId);
      setTrip(result);
      const day = result.days.find((item) => item.id === dayId);
      if (!day) {
        router.replace(`/trip/${tripId}`);
        return;
      }
      try {
        const map = await mapService.getTripMap(tripId, day.day_number);
        setMapConfig(map);
      } catch {
        setMapConfig(null);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    } finally {
      if (!opts?.silent) setLoading(false);
    }
  }

  useEffect(() => {
    load();
    setWeatherCity(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tripId, dayId]);

  useEffect(() => {
    if (!ticket) return;
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") setTicket(null);
    }
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("keydown", onKey);
    };
  }, [ticket]);

  const day = trip?.days.find((item) => item.id === dayId);
  const dayIso = trip && day ? dayDateIso(trip.start_date, day.day_number, day.date) : null;

  useEffect(() => {
    if (!weatherCity || weatherCity.latitude == null || weatherCity.longitude == null || !dayIso) {
      setWeather(null);
      return;
    }
    let cancelled = false;
    setWeatherLoading(true);
    weatherService
      .getDay(weatherCity.latitude, weatherCity.longitude, dayIso, weatherCity.name)
      .then((result) => {
        if (!cancelled) setWeather(result);
      })
      .catch(() => {
        if (!cancelled) setWeather(null);
      })
      .finally(() => {
        if (!cancelled) setWeatherLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [weatherCity, dayIso]);

  async function handleAddPlace(
    _dayId: string,
    placeId: string,
    opts?: { customEntranceFee?: number | null; partySize?: number },
  ) {
    if (!day) throw new Error(fa.errors.generic);
    const already = day.trip_places.some((tp) => tp.place_id === placeId);
    if (already && !window.confirm(fa.trip.confirmDuplicatePlace)) {
      const cancelled = new Error("cancelled");
      (cancelled as Error & { code?: string }).code = "ADD_CANCELLED";
      throw cancelled;
    }
    try {
      await tripService.addPlaceToDay(day.id, placeId, {
        allowDuplicate: already,
        customEntranceFee: opts?.customEntranceFee ?? null,
        partySize: opts?.partySize ?? trip?.traveler_count ?? 1,
      });
      await load({ silent: true });
    } catch (err) {
      if (err instanceof Error && (err as Error & { code?: string }).code === "ADD_CANCELLED") throw err;
      const message = err instanceof ApiError ? err.message : fa.errors.generic;
      setError(message);
      throw err instanceof Error ? err : new Error(message);
    }
  }

  async function handleAddStay(
    placeId: string,
    checkInDayNumber: number,
    nights: number,
    nightlyRate: number | null,
    guestCount: number,
  ) {
    const occupied = (trip?.stays ?? []).some((stay) => {
      const start = stay.check_in_day_number;
      const end = start + stay.nights;
      for (let n = 0; n < nights; n += 1) {
        const dayNumber = checkInDayNumber + n;
        if (dayNumber >= start && dayNumber < end) return true;
      }
      return false;
    });
    if (occupied) {
      setError(fa.trip.lodgingAlreadyOnDay);
      return;
    }
    try {
      await stayService.addStay(tripId, {
        place_id: placeId,
        check_in_day_number: checkInDayNumber,
        nights,
        nightly_rate: nightlyRate,
        guest_count: guestCount,
      });
      await load({ silent: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    }
  }

  async function handleRemoveStay(stayId: string) {
    try {
      await stayService.removeStay(tripId, stayId);
      await load({ silent: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    }
  }

  async function handleRemoveItem(item: DayItineraryItem) {
    if (item.kind === "stay") {
      await handleRemoveStay(item.id);
      return;
    }
    if (!day) return;
    try {
      await tripService.removeStop(day.id, item.id);
      await load({ silent: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    }
  }

  async function handleReorder(next: DayItineraryItem[]) {
    if (!day) return;
    try {
      await tripService.reorderItinerary(
        day.id,
        next.map((item) => ({ kind: item.kind, id: item.id })),
      );
      await load({ silent: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    }
  }

  if (loading) {
    return (
      <div className="container section">
        <p className="muted">{fa.common.loading}</p>
      </div>
    );
  }

  if (error && !trip) {
    return (
      <div className="container section">
        <ErrorNotice message={error} onRetry={load} />
      </div>
    );
  }

  if (!trip || !day) return null;

  const itinerary = buildDayItinerary(day, trip.stays ?? []);
  const dayHasLodging = itinerary.some((item) => item.kind === "stay");
  const sortedDays = [...trip.days].sort((a, b) => a.day_number - b.day_number);
  const dayIndex = sortedDays.findIndex((item) => item.id === dayId);
  const prevDay = dayIndex > 0 ? sortedDays[dayIndex - 1] : null;
  const nextDay = dayIndex >= 0 && dayIndex < sortedDays.length - 1 ? sortedDays[dayIndex + 1] : null;
  const initialCityId = resolvePlannerCityId(trip, day, urlCityId);
  const totalMeters = (mapConfig?.route_segments ?? []).reduce((sum, seg) => sum + (seg.distance_meters || 0), 0);
  const totalSeconds = (mapConfig?.route_segments ?? []).reduce((sum, seg) => sum + (seg.duration_seconds || 0), 0);
  const hasRoute = (mapConfig?.route_segments.length ?? 0) > 0;
  const hasPins = (mapConfig?.pins.length ?? 0) > 0;

  return (
    <div className="container container-wide section day-planner-page">
      <div className="row-between day-planner-head">
        <Link href={`/trip/${tripId}`} className="nav-text-btn">
          ← {fa.trip.backToDays}
        </Link>
        <div className="day-planner-title-row">
          {prevDay ? (
            <Link href={`/trip/${tripId}/day/${prevDay.id}`} className="day-nav-btn" aria-label={fa.trip.prevDay}>
              ‹
            </Link>
          ) : (
            <span className="day-nav-btn is-disabled" aria-hidden>
              ‹
            </span>
          )}
          <h1 className="day-planner-title">
            {formatDayOrdinal(day.day_number)}
            {dayDateIso(trip.start_date, day.day_number, day.date) ? (
              <span className="day-planner-date num">
                {" "}
                {formatJalaliSlash(dayDateIso(trip.start_date, day.day_number, day.date))}
              </span>
            ) : null}
          </h1>
          {nextDay ? (
            <Link href={`/trip/${tripId}/day/${nextDay.id}`} className="day-nav-btn" aria-label={fa.trip.nextDay}>
              ›
            </Link>
          ) : (
            <span className="day-nav-btn is-disabled" aria-hidden>
              ›
            </span>
          )}
        </div>
      </div>

      {error && (
        <div style={{ marginBottom: 12 }}>
          <ErrorNotice message={error} />
        </div>
      )}

      <div className="day-planner">
        <WeatherRail weather={weather} loading={weatherLoading} cityName={weatherCity?.name} />
        <section className="day-planner-search">
          <DestinationSearchPanel
            key={day.id}
            days={trip.days}
            lockedDay={day}
            variant="planner"
            tripId={tripId}
            initialCityId={initialCityId}
            onCityChange={setWeatherCity}
            onAddPlace={handleAddPlace}
            onAddStay={handleAddStay}
            dayHasLodging={dayHasLodging}
            defaultPartySize={trip.traveler_count ?? 1}
          />
        </section>

        <aside className="day-planner-plan">
          <DayPlanColumn
            items={itinerary}
            onReorder={handleReorder}
            onRemove={handleRemoveItem}
            onOpenTicket={() => setTicket("plan")}
          />
          <div className="day-planner-map is-preview">
            <div className="day-planner-map-stage">
              <button
                type="button"
                className="day-map-open"
                onClick={() => setTicket("map")}
                aria-label={fa.trip.expandDayMap}
              >
                <span className="day-map-open-label">{fa.trip.expandDayMap}</span>
              </button>
              {hasPins && mapConfig ? (
                <TripRouteMap config={mapConfig} className="trip-map trip-map-day" showControls={false} />
              ) : (
                <div className="trip-map trip-map-day trip-map-empty">
                  <p className="muted">{fa.trip.dayRouteEmpty}</p>
                </div>
              )}
            </div>
            <div className="day-route-totals">
              {hasRoute ? (
                <>
                  <div>
                    <span>{fa.trip.dayDistance}</span>
                    <strong>{formatDistanceKm(totalMeters / 1000) ?? fa.destination.unknownMetric}</strong>
                  </div>
                  <div>
                    <span>{fa.trip.dayDuration}</span>
                    <strong>{formatDrivingDurationShort(totalSeconds / 60) ?? fa.destination.unknownMetric}</strong>
                  </div>
                </>
              ) : (
                <p className="muted">{fa.trip.dayRouteEmpty}</p>
              )}
            </div>
          </div>
        </aside>
      </div>

      {ticket === "plan" && (
        <AppOverlay
          className="notebook-overlay day-ticket-overlay"
          role="presentation"
          onClick={() => setTicket(null)}
        >
          <div
            className="day-ticket day-ticket-plan"
            role="dialog"
            aria-modal="true"
            aria-label={fa.trip.selectedStops}
            onClick={(event) => event.stopPropagation()}
          >
            <div className="day-ticket-head">
              <p className="day-ticket-kicker">{formatDayOrdinal(day.day_number)}</p>
              <h2>{fa.trip.selectedStops}</h2>
              <button type="button" className="icon-btn" onClick={() => setTicket(null)} aria-label={fa.common.close}>
                ×
              </button>
            </div>
            <DayPlanColumn
              variant="ticket"
              items={itinerary}
              onReorder={handleReorder}
              onRemove={handleRemoveItem}
            />
          </div>
        </AppOverlay>
      )}

      {ticket === "map" && (
        <AppOverlay
          className="notebook-overlay day-ticket-overlay"
          role="presentation"
          onClick={() => setTicket(null)}
        >
          <div
            className="day-ticket day-ticket-map"
            role="dialog"
            aria-modal="true"
            aria-label={fa.trip.expandDayMap}
            onClick={(event) => event.stopPropagation()}
          >
            <div className="day-ticket-head">
              <p className="day-ticket-kicker">{formatDayOrdinal(day.day_number)}</p>
              <h2>{fa.summary.routeMap}</h2>
              <button type="button" className="icon-btn" onClick={() => setTicket(null)} aria-label={fa.common.close}>
                ×
              </button>
            </div>
            <div className="day-ticket-map-stage">
              {hasPins && mapConfig ? (
                <TripRouteMap config={mapConfig} className="trip-map trip-map-ticket" />
              ) : (
                <div className="trip-map trip-map-ticket trip-map-empty">
                  <p className="muted">{fa.trip.dayRouteEmpty}</p>
                </div>
              )}
            </div>
            <div className="day-route-totals">
              {hasRoute ? (
                <>
                  <div>
                    <span>{fa.trip.dayDistance}</span>
                    <strong>{formatDistanceKm(totalMeters / 1000) ?? fa.destination.unknownMetric}</strong>
                  </div>
                  <div>
                    <span>{fa.trip.dayDuration}</span>
                    <strong>{formatDrivingDurationShort(totalSeconds / 60) ?? fa.destination.unknownMetric}</strong>
                  </div>
                </>
              ) : (
                <p className="muted">{fa.trip.dayRouteEmpty}</p>
              )}
            </div>
          </div>
        </AppOverlay>
      )}
    </div>
  );
}
