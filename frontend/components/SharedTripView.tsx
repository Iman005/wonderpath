"use client";

import dynamic from "next/dynamic";
import fa from "@/i18n/fa";
import {
  formatDayLabel,
  formatDistanceKm,
  formatDrivingDurationShort,
  formatToman,
} from "@/shared/format";
import type { SharedTrip } from "@/shared/types";
import WeatherRangeList from "@/components/WeatherRangeList";
import EmptyState from "@/components/EmptyState";

const TripRouteMap = dynamic(() => import("@/components/TripRouteMap"), { ssr: false });

export default function SharedTripView({
  snapshot,
  readOnly = false,
}: {
  snapshot: SharedTrip;
  readOnly?: boolean;
}) {
  const { summary, budget, map, notes, packing_lists, weather } = snapshot;
  const hasMap = Boolean(map && (map.pins.length > 0 || map.route_segments.length > 0));
  const hasPlaces =
    summary.days.some((day) => day.places.length > 0) || (summary.stays?.length ?? 0) > 0;

  return (
    <div className="share-view">
      {readOnly && <p className="share-readonly">{fa.summary.readOnlyBanner}</p>}

      <div className="row-between" style={{ margin: "14px 0 24px", flexWrap: "wrap", gap: 10 }}>
        <div>
          <p className="muted" style={{ margin: "0 0 4px" }}>
            {fa.summary.title}
          </p>
          <h1 style={{ fontSize: "1.6rem", fontWeight: 800, margin: 0 }}>{snapshot.trip_name}</h1>
          {snapshot.origin_label && (
            <p className="muted">
              {fa.summary.origin}: {snapshot.origin_label}
            </p>
          )}
        </div>
        <div style={{ textAlign: "left" }}>
          <p className="muted" style={{ margin: "0 0 4px" }}>
            {fa.summary.tripTotal}
          </p>
          <p className="num" style={{ fontWeight: 700, fontSize: "1.3rem", color: "var(--terracotta)" }}>
            {formatToman(budget.grand_total)}
          </p>
        </div>
      </div>

      {(snapshot.total_distance_km != null || snapshot.total_duration_minutes != null) && (
        <div className="share-metrics">
          {snapshot.total_distance_km != null && (
            <div>
              <span>{fa.summary.totalDistance}</span>
              <strong>{formatDistanceKm(snapshot.total_distance_km)}</strong>
            </div>
          )}
          {snapshot.total_duration_minutes != null && (
            <div>
              <span>{fa.summary.totalDuration}</span>
              <strong>{formatDrivingDurationShort(snapshot.total_duration_minutes)}</strong>
            </div>
          )}
        </div>
      )}

      {hasMap && map ? (
        <>
          <h2 className="section-title">{fa.summary.routeMap}</h2>
          <TripRouteMap config={map} />
        </>
      ) : null}

      <h2 className="section-title">{fa.summary.weatherTitle}</h2>
      <WeatherRangeList days={weather} />

      {!hasPlaces ? (
        <EmptyState message={fa.summary.empty} />
      ) : (
        <div className="stack" style={{ marginTop: 18 }}>
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
                          <strong>{place.name}</strong>
                          <span className="muted"> — {place.city_name}</span>
                          {place.note && (
                            <div className="muted" style={{ fontSize: "0.85rem", marginTop: 2 }}>
                              {place.note}
                            </div>
                          )}
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
              </div>
              <span className="num muted">{formatToman(stay.total)}</span>
            </div>
          ))}
        </div>
      )}

      {notes.length > 0 && (
        <div className="card" style={{ marginTop: 16 }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 800, margin: "0 0 12px" }}>{fa.summary.notesTitle}</h2>
          {notes.map((note) => (
            <p key={note.id} style={{ whiteSpace: "pre-wrap" }}>
              {note.day_number ? `${formatDayLabel(note.day_number)}: ` : ""}
              {note.body}
            </p>
          ))}
        </div>
      )}

      {packing_lists.length > 0 && (
        <div className="card" style={{ marginTop: 16 }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 800, margin: "0 0 12px" }}>{fa.summary.packingTitle}</h2>
          {packing_lists.map((list) => (
            <div key={list.id} style={{ marginBottom: 10 }}>
              <strong>{list.title}</strong>
              <ul>
                {list.items.map((item) => (
                  <li key={item.id}>{item.label}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
