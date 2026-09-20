/** City shortcut chips under the day-planner search field. */

export type DayCitySuggestion = {
  query: string;
  label: string;
  landmark: string;
  image?: string;
  tone: string;
};

export const DAY_CITY_SUGGESTIONS: DayCitySuggestion[] = [
  {
    query: "رشت",
    label: "رشت",
    landmark: "میدان شهرداری",
    image: "/suggestions/masuleh.jpg",
    tone: "#2f9e44",
  },
  {
    query: "تهران",
    label: "تهران",
    landmark: "برج آزادی",
    image: "/suggestions/azadi.jpg",
    tone: "#1c7ed6",
  },
  {
    query: "رامسر",
    label: "مازندران",
    landmark: "کاخ رامسر",
    image: "/suggestions/ramsar.jpg",
    tone: "#0ca678",
  },
  {
    query: "بندرعباس",
    label: "بندرعباس",
    landmark: "معبد هندوها",
    image: "/suggestions/bandarabbas.jpg",
    tone: "#f08c00",
  },
  {
    query: "قشم",
    label: "قشم",
    landmark: "ژئوپارک جهانی",
    image: "/suggestions/qeshm.jpg",
    tone: "#15aabf",
  },
  {
    query: "تبریز",
    label: "تبریز",
    landmark: "ائل‌گلی",
    image: "/suggestions/tabriz.jpg",
    tone: "#4263eb",
  },
  {
    query: "شیراز",
    label: "شیراز",
    landmark: "مسجد نصیرالملک",
    image: "/suggestions/nasir.jpg",
    tone: "#e64980",
  },
  {
    query: "اصفهان",
    label: "اصفهان",
    landmark: "نقش جهان",
    image: "/suggestions/naqsh.jpg",
    tone: "#7950f2",
  },
];
