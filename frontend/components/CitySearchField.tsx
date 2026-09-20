"use client";

import { useEffect, useRef, useState } from "react";
import fa from "@/i18n/fa";
import { destinationService } from "@/services/destinationService";
import type { City } from "@/shared/types";
import { formatDistanceKm, formatDrivingDurationShort } from "@/shared/format";

export default function CitySearchField({
  label,
  placeholder,
  selected,
  onSelect,
  inputClassName = "input input-light",
  tripId,
  dayNumber,
}: {
  label?: string;
  placeholder: string;
  selected: City | null;
  onSelect: (city: City | null) => void;
  inputClassName?: string;
  tripId?: string;
  dayNumber?: number;
}) {
  const [query, setQuery] = useState(selected?.name ?? "");
  const [results, setResults] = useState<City[]>([]);
  const [searching, setSearching] = useState(false);
  const [open, setOpen] = useState(false);
  const wrapRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (selected) setQuery(selected.name);
  }, [selected]);

  useEffect(() => {
    const q = query.trim();
    if (q.length < 1 || (selected && q === selected.name)) {
      setResults([]);
      return;
    }
    const handle = window.setTimeout(async () => {
      setSearching(true);
      try {
        const cities = await destinationService.searchCities(q, tripId, dayNumber);
        setResults(cities);
        setOpen(true);
      } finally {
        setSearching(false);
      }
    }, 280);
    return () => window.clearTimeout(handle);
  }, [query, selected, tripId, dayNumber]);

  useEffect(() => {
    function onDocClick(event: MouseEvent) {
      if (!wrapRef.current?.contains(event.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  return (
    <div className="city-search" ref={wrapRef}>
      {label && <span className="setup-field-label">{label}</span>}
      <input
        className={inputClassName}
        placeholder={placeholder}
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          if (selected) onSelect(null);
        }}
        onFocus={() => {
          if (results.length > 0) setOpen(true);
        }}
        autoComplete="off"
      />
      {searching && <p className="muted city-search-status">{fa.destination.searching}</p>}
      {open && results.length > 0 && (
        <ul className="city-suggest">
          {results.map((city) => (
            <li key={city.id}>
              <button
                type="button"
                onClick={() => {
                  onSelect(city);
                  setQuery(city.name);
                  setOpen(false);
                  setResults([]);
                }}
              >
                <strong className="city-suggest-name">{city.name}</strong>
                {city.distance_from_origin_km != null && (
                  <span className="city-suggest-metrics">
                    {formatDistanceKm(city.distance_from_origin_km, city.distance_is_driving !== false)}
                    {city.distance_is_driving !== false &&
                      city.duration_from_origin_minutes != null &&
                      ` · ${formatDrivingDurationShort(city.duration_from_origin_minutes)}`}
                  </span>
                )}
                {city.province_name && <span className="city-suggest-province">{city.province_name}</span>}
              </button>
            </li>
          ))}
        </ul>
      )}
      {open && !searching && query.trim() && results.length === 0 && selected?.name !== query.trim() && (
        <p className="muted city-search-status">{fa.destination.noCitiesFound}</p>
      )}
    </div>
  );
}
