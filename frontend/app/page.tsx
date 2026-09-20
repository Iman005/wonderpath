import Link from "next/link";
import fa from "@/i18n/fa";
import LandingCta from "@/components/LandingCta";
import { TOURS } from "@/modules/tours/catalog";
import { toPersianDigits } from "@/shared/format";

const FEATURES = [
  { title: fa.landing.featureSearchTitle, body: fa.landing.featureSearchBody },
  { title: fa.landing.featureItineraryTitle, body: fa.landing.featureItineraryBody },
  { title: fa.landing.featureStayTitle, body: fa.landing.featureStayBody },
  { title: fa.landing.featureBudgetTitle, body: fa.landing.featureBudgetBody },
  { title: fa.landing.featureMapTitle, body: fa.landing.featureMapBody },
  { title: fa.landing.featureNotesTitle, body: fa.landing.featureNotesBody },
  { title: fa.landing.featureWeatherTitle, body: fa.landing.featureWeatherBody },
  { title: fa.landing.featureShareTitle, body: fa.landing.featureShareBody },
  { title: fa.landing.featureSuggestTitle, body: fa.landing.featureSuggestBody },
] as const;

const HOW = [
  { title: fa.landing.how1Title, body: fa.landing.how1Body },
  { title: fa.landing.how2Title, body: fa.landing.how2Body },
  { title: fa.landing.how3Title, body: fa.landing.how3Body },
] as const;

const STICKERS = [
  fa.landing.stickerTea,
  fa.landing.stickerMap,
  fa.landing.stickerRoute,
  fa.landing.stickerBag,
] as const;

const LANDING_TOURS = TOURS.slice(0, 4);

export default function LandingPage() {
  return (
    <>
      <section className="hero landing-hero">
        <div className="container container-wide landing-hero-inner">
          <p className="landing-kicker">{fa.landing.kicker}</p>
          <h1 className="hero-title landing-hero-title">{fa.landing.heroTitle}</h1>
          <div className="landing-cta-wrap">
            <LandingCta className="landing-cta-hero" />
          </div>
        </div>
      </section>

      <section className="section landing-intro">
        <div className="container container-wide">
          <p className="landing-intro-copy">{fa.landing.heroSubtitle}</p>
          <ul className="landing-note-row">
            {STICKERS.map((label) => (
              <li key={label}>{label}</li>
            ))}
          </ul>
          <div className="landing-photos">
            <figure className="landing-photo">
              <img src="/landing/photo-1.jpg" alt="" />
            </figure>
            <figure className="landing-photo">
              <img src="/landing/photo-2.jpg" alt="" />
            </figure>
          </div>
        </div>
      </section>

      <section className="section landing-tours">
        <div className="container container-wide">
          <div className="landing-tours-head">
            <div>
              <h2 className="section-title">{fa.landing.toursTitle}</h2>
              <p className="muted landing-tours-lead">{fa.landing.toursBody}</p>
            </div>
            <Link href="/tours" className="btn btn-outline">
              {fa.landing.toursCta}
            </Link>
          </div>
          <div className="tours-city-grid">
            {LANDING_TOURS.map((tour) => (
              <Link key={tour.id} href={`/tours/${tour.id}`} className="card tours-card">
                <img src={tour.image} alt="" className="tours-card-image" />
                <p className="tours-card-city">
                  {tour.province} · {tour.city}
                </p>
                <h3 className="tours-card-name">{tour.name}</h3>
                <p className="tours-card-meta">
                  {tour.city}{" "}
                  <span className="num">{toPersianDigits(tour.days)}</span> روز
                </p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="section landing-features">
        <div className="container container-wide">
          <h2 className="section-title">{fa.landing.featuresTitle}</h2>
          <div className="trip-grid landing-feature-grid">
            {FEATURES.map((feature) => (
              <article key={feature.title} className="card landing-feature-card">
                <h3 className="landing-feature-title">{feature.title}</h3>
                <p className="muted landing-feature-body">{feature.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section landing-how">
        <div className="container container-wide">
          <h2 className="section-title">{fa.landing.howTitle}</h2>
          <div className="landing-how-grid">
            {HOW.map((item, index) => (
              <article key={item.title} className="card landing-how-card">
                <span className="landing-how-num num">{index + 1}</span>
                <h3>{item.title}</h3>
                <p className="muted">{item.body}</p>
              </article>
            ))}
          </div>
          <p className="landing-guide-link">
            <Link href="/guide">{fa.landing.guideCta}</Link>
          </p>
        </div>
      </section>
    </>
  );
}
