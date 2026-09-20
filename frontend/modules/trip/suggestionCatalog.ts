/** Local banner photos — stored in /public/suggestions, never fetched live. */

export type SuggestionItem = {
  name: string;
  city: string;
  province: string;
  blurb: string;
  image: string;
};

export const SUGGESTIONS: SuggestionItem[] = [
  {
    name: "مسجد نصیرالملک",
    city: "شیراز",
    province: "فارس",
    blurb: "مسجد صورتی شیراز؛ نور صبحگاهی از شیشه‌های رنگی.",
    image: "/suggestions/nasir.jpg",
  },
  {
    name: "حافظیه",
    city: "شیراز",
    province: "فارس",
    blurb: "آرامگاه حافظ در باغ شیراز؛ مناسب یک عصر آرام.",
    image: "/suggestions/hafez.jpg",
  },
  {
    name: "تخت جمشید",
    city: "مرودشت",
    province: "فارس",
    blurb: "پایتخت باستانی هخامنشیان، میراث جهانی یونسکو.",
    image: "/suggestions/persepolis.jpg",
  },
  {
    name: "میدان نقش جهان",
    city: "اصفهان",
    province: "اصفهان",
    blurb: "قلب تاریخی اصفهان با مسجدها و بازار پیرامون میدان.",
    image: "/suggestions/naqsh.jpg",
  },
  {
    name: "سی‌وسه‌پل",
    city: "اصفهان",
    province: "اصفهان",
    blurb: "پل تاریخی زاینده‌رود؛ پیاده‌روی عصرگاهی روی ۳۳ دهانه.",
    image: "/suggestions/siose.jpg",
  },
  {
    name: "بافت تاریخی یزد",
    city: "یزد",
    province: "یزد",
    blurb: "خشت، بادگیر و کوچه‌های سایه‌دار بزرگ‌ترین بافت خشتی جهان.",
    image: "/suggestions/yazd.jpg",
  },
  {
    name: "باغ شاهزاده ماهان",
    city: "ماهان",
    province: "کرمان",
    blurb: "باغ ایرانی پلکانی در دامنه جوپار.",
    image: "/suggestions/shazdeh.jpg",
  },
  {
    name: "ماسوله",
    city: "ماسوله",
    province: "گیلان",
    blurb: "روستای پلکانی جنگلی؛ پشت‌بام یکی حیاط دیگری است.",
    image: "/suggestions/masuleh.jpg",
  },
  {
    name: "برج آزادی",
    city: "تهران",
    province: "تهران",
    blurb: "نماد مدرن تهران در ورودی غربی شهر.",
    image: "/suggestions/azadi.jpg",
  },
];
