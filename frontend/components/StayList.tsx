"use client";

import fa from "@/i18n/fa";
import { formatToman, toPersianDigits } from "@/shared/format";
import type { TripStay } from "@/shared/types";

export default function StayList({
  stays,
  onRemove,
}: {
  stays: TripStay[];
  onRemove: (stayId: string) => Promise<void>;
}) {
  return (
    <section className="stay-list">
      <h2 className="section-title" style={{ margin: "0 0 10px" }}>
        {fa.trip.staysTitle}
      </h2>
      {stays.length === 0 ? (
        <p className="muted" style={{ fontSize: "0.9rem" }}>
          {fa.trip.staysEmpty}
        </p>
      ) : (
        stays.map((stay) => (
          <article key={stay.id} className="stay-card">
            <div>
              <p className="stay-card-name">{stay.place_name || fa.budget.unnamedPlace}</p>
              <p className="stay-card-meta">
                {fa.trip.stayNights
                  .replace("{nights}", toPersianDigits(stay.nights))
                  .replace("{day}", toPersianDigits(stay.check_in_day_number))}
                {stay.city_name ? ` · ${stay.city_name}` : ""}
              </p>
              <p className="stay-card-rate num">
                {stay.nightly_rate == null
                  ? fa.trip.stayUnknownRate
                  : `${formatToman(stay.nightly_rate)} × ${toPersianDigits(stay.nights)}`}
              </p>
            </div>
            <button
              className="icon-btn danger"
              type="button"
              aria-label={fa.trip.removeStay}
              onClick={() => onRemove(stay.id)}
            >
              ×
            </button>
          </article>
        ))
      )}
    </section>
  );
}
