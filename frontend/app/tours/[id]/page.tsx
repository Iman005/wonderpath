import Link from "next/link";
import { notFound } from "next/navigation";
import fa from "@/i18n/fa";
import LandingCta from "@/components/LandingCta";
import { getTour } from "@/modules/tours/catalog";
import { toPersianDigits } from "@/shared/format";

export default function TourDetailPage({ params }: { params: { id: string } }) {
  const tour = getTour(params.id);
  if (!tour) notFound();

  return (
    <section className="section tours-page">
      <div className="container tours-detail">
        <Link href="/tours" className="nav-text-btn">
          ← {fa.tours.backList}
        </Link>
        <figure className="tours-detail-hero">
          <img src={tour.image} alt="" />
        </figure>
        <p className="tours-kicker">
          {tour.province} · {tour.city}
        </p>
        <h1 className="tours-page-title">{tour.name}</h1>
        <p className="muted tours-lead">{tour.summary}</p>
        <p className="tours-card-meta">
          {tour.city}{" "}
          <span className="num">{toPersianDigits(tour.days)}</span> روز
        </p>
        <ul className="tours-highlights">
          {tour.highlights.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
        <ol className="tours-itinerary">
          {tour.itinerary.map((day) => (
            <li key={day.day}>
              <strong>
                {fa.tours.dayLabel.replace("{n}", toPersianDigits(day.day))} — {day.title}
              </strong>
              <p className="muted">{day.body}</p>
            </li>
          ))}
        </ol>
        <div className="tours-detail-cta">
          <p className="muted">
            {fa.tours.useAsPlan}{" "}
            <LandingCta planId={tour.id} className="landing-cta-inline" />
          </p>
        </div>
      </div>
    </section>
  );
}
