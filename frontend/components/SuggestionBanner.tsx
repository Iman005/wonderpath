"use client";

import { useEffect, useState } from "react";
import fa from "@/i18n/fa";
import { SUGGESTIONS } from "@/modules/trip/suggestionCatalog";

export default function SuggestionBanner({ variant = "box" }: { variant?: "box" | "backdrop" }) {
  const [index, setIndex] = useState(0);
  const places = SUGGESTIONS;

  useEffect(() => {
    if (places.length < 2) return;
    const timer = window.setInterval(() => {
      setIndex((current) => (current + 1) % places.length);
    }, 6500);
    return () => window.clearInterval(timer);
  }, [places.length]);

  const current = places[index];
  if (!current) return null;

  if (variant === "backdrop") {
    return (
      <section className="suggest-backdrop" aria-label={fa.home.suggestionsTitle}>
        {places.map((place, i) => (
          <img
            key={place.image}
            src={place.image}
            alt=""
            className={`suggest-backdrop-image${i === index ? " is-active" : ""}`}
          />
        ))}
        <div className="suggest-backdrop-shade" />
        <div className="suggest-backdrop-copy">
          <p className="suggest-banner-kicker">
            {current.city}
            {current.province ? ` · ${current.province}` : ""}
          </p>
          <h2>{current.name}</h2>
        </div>
        <div className="suggest-dots" role="tablist" aria-label={fa.home.suggestionsTitle}>
          {places.map((place, i) => (
            <button
              key={place.image}
              type="button"
              className={`suggest-dot${i === index ? " is-active" : ""}`}
              aria-label={place.name}
              onClick={() => setIndex(i)}
            />
          ))}
        </div>
      </section>
    );
  }

  return (
    <section className="suggest-box" aria-label={fa.home.suggestionsTitle}>
      <div className="suggest-box-head">
        <h2>{fa.home.suggestionsTitle}</h2>
        <p className="muted">{fa.home.suggestionsHint}</p>
      </div>
      <div className="suggest-banner">
        <img src={current.image} alt="" className="suggest-banner-image" />
        <div className="suggest-banner-copy">
          <p className="suggest-banner-kicker">
            {current.city}
            {current.province ? ` · ${current.province}` : ""}
          </p>
          <h3>{current.name}</h3>
          <p>{current.blurb}</p>
        </div>
      </div>
      <div className="suggest-dots" role="tablist" aria-label={fa.home.suggestionsTitle}>
        {places.map((place, i) => (
          <button
            key={place.image}
            type="button"
            className={`suggest-dot${i === index ? " is-active" : ""}`}
            aria-label={place.name}
            onClick={() => setIndex(i)}
          />
        ))}
      </div>
    </section>
  );
}
