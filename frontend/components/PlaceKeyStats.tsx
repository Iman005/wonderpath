"use client";

import fa from "@/i18n/fa";
import {
  formatDistanceKm,
  formatDrivingDurationShort,
  formatToman,
} from "@/shared/format";

/** Prominent distance / duration / fee row — same visual weight for all three. */
export default function PlaceKeyStats({
  distanceKm,
  durationMinutes,
  isDriving = true,
  fee,
  feeLabel,
  compact = false,
}: {
  distanceKm?: number | null;
  durationMinutes?: number | null;
  isDriving?: boolean;
  fee?: number | null;
  feeLabel?: string;
  compact?: boolean;
}) {
  const distance = formatDistanceKm(distanceKm, isDriving);
  const duration = isDriving ? formatDrivingDurationShort(durationMinutes) : null;

  return (
    <div className={`place-key-stats${compact ? " is-compact" : ""}`}>
      <div className="place-key-stat">
        <span className="place-key-stat-label">{fa.destination.distanceFromOrigin}:</span>
        <span className="place-key-stat-value">{distance ?? fa.destination.unknownMetric}</span>
      </div>
      <div className="place-key-stat">
        <span className="place-key-stat-label">{fa.destination.durationFromOrigin}:</span>
        <span className="place-key-stat-value">{duration ?? fa.destination.unknownMetric}</span>
      </div>
      <div className="place-key-stat place-key-stat-fee">
        <span className="place-key-stat-label">{feeLabel ?? fa.destination.entranceFee}:</span>
        <span className="place-key-stat-value num">{formatToman(fee)}</span>
      </div>
    </div>
  );
}
