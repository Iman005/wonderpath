"use client";

import fa from "@/i18n/fa";
import { toPersianDigits } from "@/shared/format";
import type { DayWeather } from "@/shared/types";

function weatherGlyph(code: number | null, available: boolean): string {
  if (!available || code == null) return "◌";
  if (code === 0 || code === 1) return "☀";
  if (code === 2 || code === 3) return "☁";
  if (code === 45 || code === 48) return "〰";
  if (code >= 71 && code <= 86) return "❄";
  if (code >= 95) return "⚡";
  if (code >= 50) return "☂";
  return "☀";
}

export default function WeatherRail({
  weather,
  loading,
  cityName,
}: {
  weather: DayWeather | null;
  loading: boolean;
  cityName?: string | null;
}) {
  return (
    <aside className="weather-rail" aria-label={fa.weather.title}>
      <p className="weather-rail-kicker">{fa.weather.title}</p>
      {loading ? (
        <p className="muted weather-rail-empty">{fa.weather.loading}</p>
      ) : !weather ? (
        <p className="muted weather-rail-empty">{fa.weather.pickCity}</p>
      ) : (
        <>
          <div className="weather-rail-hero">
            <span className="weather-rail-glyph" aria-hidden>
              {weatherGlyph(weather.condition_code, weather.available)}
            </span>
            <strong>{weather.condition_label}</strong>
            {(weather.city_label || cityName) && (
              <span className="muted">{weather.city_label || cityName}</span>
            )}
          </div>
          {weather.available && weather.temp_min_c != null && weather.temp_max_c != null && (
            <p className="weather-rail-temp num">
              {toPersianDigits(Math.round(weather.temp_min_c))}° — {toPersianDigits(Math.round(weather.temp_max_c))}°
            </p>
          )}
          {weather.available && weather.precipitation_probability != null && (
            <p className="muted">
              {fa.weather.rain}:{" "}
              <span className="num">{toPersianDigits(weather.precipitation_probability)}٪</span>
            </p>
          )}
          {weather.hint && <p className="weather-rail-hint">{weather.hint}</p>}
          {weather.suitable.length > 0 && (
            <div className="weather-rail-list is-good">
              <p>{fa.weather.suitable}</p>
              <ul>
                {weather.suitable.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          )}
          {weather.unsuitable.length > 0 && (
            <div className="weather-rail-list is-bad">
              <p>{fa.weather.unsuitable}</p>
              <ul>
                {weather.unsuitable.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </aside>
  );
}
