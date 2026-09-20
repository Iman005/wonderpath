"use client";

import fa from "@/i18n/fa";
import { formatJalaliSlash, toPersianDigits } from "@/shared/format";
import type { DayWeather } from "@/shared/types";

export default function WeatherRangeList({ days }: { days: DayWeather[] }) {
  if (days.length === 0) {
    return <p className="muted">{fa.summary.weatherEmpty}</p>;
  }

  return (
    <div className="weather-range">
      {days.map((day) => (
        <article key={day.date} className="weather-range-card">
          <p className="weather-range-date num">{formatJalaliSlash(day.date)}</p>
          {day.city_label && <p className="muted">{day.city_label}</p>}
          <strong>{day.condition_label}</strong>
          {day.available && day.temp_min_c != null && day.temp_max_c != null && (
            <p className="num">
              {toPersianDigits(Math.round(day.temp_min_c))}° — {toPersianDigits(Math.round(day.temp_max_c))}°
            </p>
          )}
          {day.hint && <p className="muted">{day.hint}</p>}
          {day.suitable.length > 0 && (
            <p className="weather-range-line">
              {fa.weather.suitable}: {day.suitable.slice(0, 2).join("، ")}
            </p>
          )}
          {day.unsuitable.length > 0 && (
            <p className="weather-range-line is-warn">
              {fa.weather.unsuitable}: {day.unsuitable.slice(0, 2).join("، ")}
            </p>
          )}
        </article>
      ))}
    </div>
  );
}
