"use client";

import { useState } from "react";
import fa from "@/i18n/fa";
import { formatToman, formatDayLabel, toPersianDigits } from "@/shared/format";
import { getCachedPlace } from "@/modules/trip/placeCache";
import type { Place, TripDay } from "@/shared/types";
import PlaceDetailModal from "@/components/PlaceDetailModal";

export default function DayColumn({
  day,
  onReorder,
  onRemove,
}: {
  day: TripDay;
  onReorder: (dayId: string, orderedTripPlaceIds: string[]) => Promise<void>;
  onRemove: (dayId: string, placeId: string) => Promise<void>;
}) {
  const sorted = [...day.trip_places].sort((a, b) => a.order_index - b.order_index);
  const [detailPlace, setDetailPlace] = useState<Place | null>(null);

  async function move(index: number, direction: -1 | 1) {
    const target = index + direction;
    if (target < 0 || target >= sorted.length) return;
    const ids = sorted.map((tp) => tp.id);
    [ids[index], ids[target]] = [ids[target], ids[index]];
    await onReorder(day.id, ids);
  }

  function openPlace(placeId: string) {
    const cached = getCachedPlace(placeId);
    setDetailPlace(
      cached ?? {
        id: placeId,
        name: "مکان",
        description: null,
        category: null,
        city_id: "",
        latitude: 0,
        longitude: 0,
        image: null,
        address: null,
        estimated_entrance_fee: null,
        opening_hours: null,
      },
    );
  }

  return (
    <div className="day-column" data-tone={(day.day_number - 1) % 3}>
      <div className="day-column-header">
        <span className="day-column-title">{formatDayLabel(day.day_number)}</span>
        <span className="chip">
          {toPersianDigits(sorted.length)} توقف
        </span>
      </div>

      {sorted.length === 0 ? (
        <p className="muted" style={{ fontSize: "0.9rem" }}>
          {fa.trip.dayEmpty}
        </p>
      ) : (
        <div className="route-stitch">
          {sorted.map((tp, index) => {
            const place = getCachedPlace(tp.place_id);
            const fee = tp.custom_entrance_fee ?? place?.estimated_entrance_fee ?? null;
            const name = place?.name || tp.place_name || "مکان (نام در دسترس نیست)";
            const category = place?.category;
            const kind = tp.place_kind || place?.kind;
            return (
              <div className="stop" key={tp.id}>
                <span className="stop-marker">{toPersianDigits(index + 1)}</span>
                <div className="stop-card">
                  <button type="button" className="stop-open" onClick={() => openPlace(tp.place_id)}>
                    <p className="stop-name">{name}</p>
                    {(category || kind === "dining") && (
                      <p className="stop-fee">{kind === "dining" ? fa.destination.tabDining : category}</p>
                    )}
                  </button>
                  <div className="stop-meta">
                    <span className="stop-fee num">{formatToman(fee)}</span>
                    <div className="stop-actions">
                      <button
                        className="icon-btn"
                        aria-label={fa.trip.moveUp}
                        onClick={() => move(index, -1)}
                        disabled={index === 0}
                      >
                        ↑
                      </button>
                      <button
                        className="icon-btn"
                        aria-label={fa.trip.moveDown}
                        onClick={() => move(index, 1)}
                        disabled={index === sorted.length - 1}
                      >
                        ↓
                      </button>
                      <button
                        className="icon-btn danger"
                        aria-label={fa.trip.removePlace}
                        onClick={() => onRemove(day.id, tp.place_id)}
                      >
                        ×
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {detailPlace && (
        <PlaceDetailModal
          initialPlace={detailPlace}
          days={[day]}
          allowAdd={false}
          onClose={() => setDetailPlace(null)}
        />
      )}
    </div>
  );
}
