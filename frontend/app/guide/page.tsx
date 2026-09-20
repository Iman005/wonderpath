import GuideBackLink from "@/components/GuideBackLink";
import fa from "@/i18n/fa";

const STEPS = [
  {
    title: fa.guide.step1Title,
    body: fa.guide.step1Body,
    shot: "suggest",
    caption: "خانه — بنر پیشنهاد و ساخت سفر",
  },
  {
    title: fa.guide.step2Title,
    body: fa.guide.step2Body,
    shot: "hub",
    caption: "هاب سفر — روزها، مبدأ و سقف هزینه",
  },
  {
    title: fa.guide.step3Title,
    body: fa.guide.step3Body,
    shot: "day",
    caption: "پنل روز — هوا، جست‌وجو و برنامه",
  },
  {
    title: fa.guide.step4Title,
    body: fa.guide.step4Body,
    shot: "share",
    caption: "خلاصه و اشتراک فقط‌خواندنی",
  },
] as const;

export default function GuidePage() {
  return (
    <section className="section">
      <div className="container container-wide">
        <GuideBackLink />
        <h1 className="guide-title">{fa.guide.title}</h1>
        <p className="muted guide-lead">{fa.guide.subtitle}</p>
        <div className="guide-steps">
          {STEPS.map((step) => (
            <article key={step.title} className="guide-step">
              <div>
                <h2>{step.title}</h2>
                <p>{step.body}</p>
              </div>
              <figure className={`guide-shot is-${step.shot}`}>
                {step.shot === "suggest" && (
                  <div className="guide-fake">
                    <div className="guide-fake-banner">حافظیه · شیراز</div>
                    <div className="guide-fake-row">
                      <i />
                      <i />
                    </div>
                  </div>
                )}
                {step.shot === "hub" && (
                  <div className="guide-fake">
                    <div className="guide-fake-days">
                      <b>روز ۱</b>
                      <b>روز ۲</b>
                      <b>روز ۳</b>
                    </div>
                    <div className="guide-fake-bar" />
                  </div>
                )}
                {step.shot === "day" && (
                  <div className="guide-fake is-day">
                    <aside>☀ ۲۸°</aside>
                    <div className="guide-fake-grid">
                      <span />
                      <span />
                      <span />
                      <span />
                    </div>
                    <div className="guide-fake-plan" />
                  </div>
                )}
                {step.shot === "share" && (
                  <div className="guide-fake">
                    <div className="guide-fake-map" />
                    <p>خلاصه · هزینه · هوا · یادداشت</p>
                  </div>
                )}
                <figcaption>{step.caption}</figcaption>
              </figure>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
