"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import dynamic from "next/dynamic";
import Link from "next/link";
import fa from "@/i18n/fa";
import { summaryService } from "@/services/summaryService";
import { mapService } from "@/services/mapService";
import { weatherService } from "@/services/weatherService";
import { ApiError } from "@/services/apiClient";
import { formatToman, formatDayLabel } from "@/shared/format";
import type { DayWeather, MapViewConfig, TripSummary } from "@/shared/types";
import ErrorNotice from "@/components/ErrorNotice";
import EmptyState from "@/components/EmptyState";
import WeatherRangeList from "@/components/WeatherRangeList";

const TripRouteMap = dynamic(() => import("@/components/TripRouteMap"), { ssr: false });

export default function TripSummaryPage() {
  const params = useParams<{ id: string }>();
  const tripId = params.id;

  const [summary, setSummary] = useState<TripSummary | null>(null);
  const [mapConfig, setMapConfig] = useState<MapViewConfig | null>(null);
  const [weather, setWeather] = useState<DayWeather[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mapError, setMapError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    setMapError(null);
    try {
      const [summaryResult, mapResult, weatherResult] = await Promise.all([
        summaryService.getTripSummary(tripId),
        mapService.getTripMap(tripId).catch((err) => {
          setMapError(err instanceof ApiError ? err.message : fa.summary.mapUnavailable);
          return null;
        }),
        weatherService.getTripWeather(tripId).catch(() => []),
      ]);
      setSummary(summaryResult);
      setMapConfig(mapResult);
      setWeather(weatherResult);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : fa.errors.generic);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tripId]);

  const hasAnyPlaces =
    (summary?.days.some((d) => d.places.length > 0) ?? false) || (summary?.stays?.length ?? 0) > 0;
  const hasMap = Boolean(mapConfig && (mapConfig.pins.length > 0 || mapConfig.route_segments.length > 0));

  return (
    <div className="container section">
      <Link href={`/trip/${tripId}`} className="nav-text-btn">
        ← {fa.trip.backToTrip}
      </Link>

      {loading && <p className="muted" style={{ marginTop: 14 }}>{fa.common.loading}</p>}
      {error && (
        <div style={{ marginTop: 14 }}>
          <ErrorNotice message={error} onRetry={load} />
        </div>
      )}

      {summary && (
        <>
          <div className="row-between" style={{ margin: "14px 0 24px", flexWrap: "wrap", gap: 10 }}>
            <div>
              <p className="muted" style={{ margin: "0 0 4px" }}>
                {fa.summary.title}
              </p>
              <h1 style={{ fontSize: "1.6rem", fontWeight: 800, margin: 0 }}>{summary.trip_name}</h1>
            </div>
            <div style={{ textAlign: "left" }}>
              <p className="muted" style={{ margin: "0 0 4px" }}>
                {fa.summary.tripTotal}
              </p>
              <p className="num" style={{ fontWeight: 700, fontSize: "1.3rem", color: "var(--terracotta)" }}>
                {formatToman(summary.estimated_trip_total)}
              </p>
            </div>
          </div>

          {(hasMap || mapError) && (
            <>
              <h2 className="section-title">{fa.summary.routeMap}</h2>
              {mapError && <p className="muted" style={{ marginBottom: 16 }}>{mapError}</p>}
              {hasMap && mapConfig ? (
                <>
                  <TripRouteMap config={mapConfig} />
                  <div className="map-legend">
                    <span className="map-legend-item">
                      <i className="map-legend-swatch is-current" />
                      {fa.summary.currentLeg}
                    </span>
                    <span className="map-legend-item">
                      <i className="map-legend-swatch is-other" />
                      {fa.summary.otherLegs}
                    </span>
                    <span className="muted">{fa.summary.mapLegend}</span>
                  </div>
                </>
              ) : null}
            </>
          )}

          <h2 className="section-title">{fa.summary.weatherTitle}</h2>
          <WeatherRangeList days={weather} />

          {!hasAnyPlaces ? (
            <EmptyState message={fa.summary.empty} />
          ) : (
            <div className="stack">
              {summary.days
                .sort((a, b) => a.day_number - b.day_number)
                .map((day) => (
                  <div className="card" key={day.trip_day_id}>
                    <div className="row-between" style={{ marginBottom: 12 }}>
                      <h2 style={{ fontSize: "1.1rem", fontWeight: 800, margin: 0 }}>
                        {formatDayLabel(day.day_number)}
                      </h2>
                      <span className="muted">
                        {fa.summary.dayTotal}: <span className="num">{formatToman(day.estimated_day_total)}</span>
                      </span>
                    </div>

                    {day.places.length === 0 ? (
                      <p className="muted" style={{ fontSize: "0.9rem" }}>
                        {fa.trip.dayEmpty}
                      </p>
                    ) : (
                      <ol style={{ margin: 0, paddingInlineStart: "1.2em" }}>
                        {day.places
                          .sort((a, b) => a.order_index - b.order_index)
                          .map((place) => (
                            <li key={`${day.trip_day_id}-${place.order_index}`} style={{ marginBottom: 10 }}>
                              <div className="row-between">
                                <div>
                                  <strong>{place.name}</strong>
                                  <span className="muted"> — {place.city_name}</span>
                                  {place.category && <span className="muted"> · {place.category}</span>}
                                  {place.note && (
                                    <div className="muted" style={{ fontSize: "0.85rem", marginTop: 2 }}>
                                      {place.note}
                                    </div>
                                  )}
                                </div>
                                <span className="num muted">{formatToman(place.estimated_entrance_fee)}</span>
                              </div>
                            </li>
                          ))}
                      </ol>
                    )}
                  </div>
                ))}
            </div>
          )}

          {(summary.stays ?? []).length > 0 && (
            <div className="card" style={{ marginTop: 16 }}>
              <h2 style={{ fontSize: "1.1rem", fontWeight: 800, margin: "0 0 12px" }}>
                {fa.summary.staysTitle}
              </h2>
              {(summary.stays ?? []).map((stay) => (
                <div className="row-between" key={stay.stay_id} style={{ marginBottom: 10 }}>
                  <div>
                    <strong>{stay.name}</strong>
                    {stay.city_name && <span className="muted"> — {stay.city_name}</span>}
                    <div className="muted" style={{ fontSize: "0.85rem", marginTop: 2 }}>
                      {fa.trip.stayNights
                        .replace("{nights}", String(stay.nights))
                        .replace("{day}", String(stay.check_in_day_number))}
                    </div>
                  </div>
                  <span className="num muted">{formatToman(stay.total)}</span>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
