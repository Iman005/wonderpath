"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import fa from "@/i18n/fa";
import { toPersianDigits } from "@/shared/format";
import { listProvinces, TOURS, type Tour } from "@/modules/tours/catalog";

const MATRIX_ROWS = 3;

function CompactPlanCard({ plan }: { plan: Tour }) {
  return (
    <Link href={`/tours/${plan.id}`} className="card tours-card is-compact">
      <img src={plan.image} alt="" className="tours-card-image" />
      <span className="tours-card-copy">
        <span className="tours-card-name">{plan.name}</span>
        <span className="tours-card-meta">
          {plan.city}{" "}
          <span className="num">{toPersianDigits(plan.days)}</span> روز
        </span>
      </span>
    </Link>
  );
}

export default function ToursBrowse() {
  const [province, setProvince] = useState<string | null>(null);
  const provinces = listProvinces();
  const plans = useMemo(
    () => (province ? TOURS.filter((tour) => tour.province === province) : TOURS),
    [province],
  );
  const columns = Math.max(1, Math.ceil(plans.length / MATRIX_ROWS));

  return (
    <>
      <nav className="tours-filter" aria-label={fa.tours.filterLabel}>
        <button
          type="button"
          className={`tours-filter-chip${province === null ? " is-active" : ""}`}
          onClick={() => setProvince(null)}
        >
          {fa.tours.allProvinces}
        </button>
        {provinces.map((name) => (
          <button
            key={name}
            type="button"
            className={`tours-filter-chip${province === name ? " is-active" : ""}`}
            onClick={() => setProvince(name)}
          >
            {name}
          </button>
        ))}
      </nav>

      <div
        className="tours-matrix"
        style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}
      >
        {plans.map((plan) => (
          <CompactPlanCard key={plan.id} plan={plan} />
        ))}
      </div>
    </>
  );
}
