import Link from "next/link";
import fa from "@/i18n/fa";
import ToursBrowse from "@/components/ToursBrowse";

export default function ToursPage() {
  return (
    <section className="section tours-page">
      <div className="container container-wide">
        <Link href="/" className="nav-text-btn">
          ← {fa.tours.backLanding}
        </Link>
        <p className="tours-kicker">{fa.tours.kicker}</p>
        <h1 className="tours-page-title">{fa.tours.title}</h1>
        <p className="muted tours-lead">{fa.tours.subtitle}</p>
        <ToursBrowse />
      </div>
    </section>
  );
}
