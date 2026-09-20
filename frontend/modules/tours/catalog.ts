/** Curated sample tours for browsing — not bookings. Grouped by province/city. */

export type TourStop = {
  city: string;
  placeName: string;
};

export type TourDay = {
  day: number;
  title: string;
  body: string;
  stops: TourStop[];
};

export type Tour = {
  id: string;
  name: string;
  province: string;
  city: string;
  days: number;
  summary: string;
  image: string;
  highlights: string[];
  itinerary: TourDay[];
};

export const TOURS: Tour[] = [
  {
    id: "shiraz-classic",
    name: "شیراز کلاسیک",
    province: "فارس",
    city: "شیراز",
    days: 3,
    summary: "باغ، شعر و بافت تاریخی شیراز در سه روز آرام.",
    image: "/suggestions/nasir.jpg",
    highlights: ["مسجد نصیرالملک", "حافظیه", "باغ ارم"],
    itinerary: [
      {
        day: 1,
        title: "بافت کهنه و مسجد صورتی",
        body: "بازار وکیل، مسجد نصیرالملک و شاه‌چراغ.",
        stops: [
          { city: "شیراز", placeName: "بازار وکیل" },
          { city: "شیراز", placeName: "مسجد نصیرالملک" },
          { city: "شیراز", placeName: "شاهچراغ" },
        ],
      },
      {
        day: 2,
        title: "شعر و باغ",
        body: "حافظیه، سعدیه و باغ ارم.",
        stops: [
          { city: "شیراز", placeName: "حافظیه" },
          { city: "شیراز", placeName: "سعدیه" },
          { city: "شیراز", placeName: "باغ ارم" },
        ],
      },
      {
        day: 3,
        title: "اطراف شهر",
        body: "ارگ کریم‌خان و نارنجستان قوام.",
        stops: [
          { city: "شیراز", placeName: "ارگ کریم‌خان" },
          { city: "شیراز", placeName: "نارنجستان قوام" },
        ],
      },
    ],
  },
  {
    id: "persepolis-pasargadae",
    name: "تخت جمشید و پاسارگاد",
    province: "فارس",
    city: "مرودشت",
    days: 2,
    summary: "میراث هخامنشی در یک مسیر کوتاه بیرون شیراز.",
    image: "/suggestions/persepolis.jpg",
    highlights: ["تخت جمشید", "آرامگاه کوروش"],
    itinerary: [
      {
        day: 1,
        title: "تخت جمشید",
        body: "بازدید کامل محوطه.",
        stops: [{ city: "مرودشت", placeName: "تخت جمشید" }],
      },
      {
        day: 2,
        title: "پاسارگاد",
        body: "آرامگاه کوروش در دشت پاسارگاد.",
        stops: [{ city: "پاسارگاد", placeName: "آرامگاه کوروش" }],
      },
    ],
  },
  {
    id: "isfahan-naqsh",
    name: "اصفهان نقش جهان",
    province: "اصفهان",
    city: "اصفهان",
    days: 3,
    summary: "میدان، پل‌ها و بازار بزرگ اصفهان.",
    image: "/suggestions/naqsh.jpg",
    highlights: ["نقش جهان", "سی‌وسه‌پل", "بازار قیصریه"],
    itinerary: [
      {
        day: 1,
        title: "میدان نقش جهان",
        body: "مسجد امام و عالی‌قاپو.",
        stops: [
          { city: "اصفهان", placeName: "میدان نقش جهان" },
          { city: "اصفهان", placeName: "مسجد امام اصفهان" },
          { city: "اصفهان", placeName: "کاخ عالی‌قاپو" },
        ],
      },
      {
        day: 2,
        title: "زاینده‌رود",
        body: "سی‌وسه‌پل و خواجو در عصر.",
        stops: [
          { city: "اصفهان", placeName: "سی‌وسه‌پل" },
          { city: "اصفهان", placeName: "پل خواجو" },
        ],
      },
      {
        day: 3,
        title: "جلفا و کاخ",
        body: "کلیسای وانک و چهل‌ستون.",
        stops: [
          { city: "اصفهان", placeName: "کلیسای وانک" },
          { city: "اصفهان", placeName: "کاخ چهل‌ستون اصفهان" },
        ],
      },
    ],
  },
  {
    id: "yazd-adobe",
    name: "یزد خشتی",
    province: "یزد",
    city: "یزد",
    days: 2,
    summary: "بادگیر، کوچه و آتشکده در بزرگ‌ترین بافت خشتی.",
    image: "/suggestions/yazd.jpg",
    highlights: ["بافت تاریخی", "امیرچخماق", "آتشکده"],
    itinerary: [
      {
        day: 1,
        title: "مرکز تاریخی",
        body: "امیرچخماق و بافت خشتی.",
        stops: [
          { city: "یزد", placeName: "مجموعه امیرچخماق" },
          { city: "یزد", placeName: "بافت تاریخی یزد" },
        ],
      },
      {
        day: 2,
        title: "آتشکده و دخمه",
        body: "آتشکده و برج خاموشان.",
        stops: [
          { city: "یزد", placeName: "آتشکده یزد" },
          { city: "یزد", placeName: "برج خاموشان" },
        ],
      },
    ],
  },
  {
    id: "kerman-mahan",
    name: "کرمان و ماهان",
    province: "کرمان",
    city: "ماهان",
    days: 2,
    summary: "باغ ایرانی ماهان در کنار گشت شهری کرمان.",
    image: "/suggestions/shazdeh.jpg",
    highlights: ["باغ شاهزاده", "گنجعلی‌خان", "ماهان"],
    itinerary: [
      {
        day: 1,
        title: "کرمان",
        body: "مجموعه گنجعلی‌خان.",
        stops: [{ city: "کرمان", placeName: "گنجعلی‌خان" }],
      },
      {
        day: 2,
        title: "ماهان",
        body: "باغ شاهزاده ماهان.",
        stops: [{ city: "ماهان", placeName: "باغ شاهزاده ماهان" }],
      },
    ],
  },
  {
    id: "gilan-masuleh",
    name: "رشت و ماسوله",
    province: "گیلان",
    city: "رشت",
    days: 3,
    summary: "شهر باران، بازار محلی و روستای پلکانی جنگلی.",
    image: "/suggestions/masuleh.jpg",
    highlights: ["میدان شهرداری", "ماسوله", "بازار رشت"],
    itinerary: [
      {
        day: 1,
        title: "رشت",
        body: "میدان شهرداری، بازار بزرگ و موزه میراث روستایی.",
        stops: [
          { city: "رشت", placeName: "میدان شهرداری رشت" },
          { city: "رشت", placeName: "بازار بزرگ رشت" },
          { city: "رشت", placeName: "موزه میراث روستایی گیلان" },
        ],
      },
      {
        day: 2,
        title: "ماسوله",
        body: "پیاده‌روی در روستای پلکانی.",
        stops: [{ city: "ماسوله", placeName: "ماسوله" }],
      },
      {
        day: 3,
        title: "انزلی",
        body: "تالاب انزلی.",
        stops: [{ city: "بندر انزلی", placeName: "تالاب انزلی" }],
      },
    ],
  },
  {
    id: "tehran-one",
    name: "تهران یک‌روزه",
    province: "تهران",
    city: "تهران",
    days: 1,
    summary: "نمادهای شهری پایتخت در یک برنامه فشرده.",
    image: "/suggestions/azadi.jpg",
    highlights: ["برج آزادی", "موزه ملی", "تجریش"],
    itinerary: [
      {
        day: 1,
        title: "غرب تا شمال شهر",
        body: "آزادی، موزه ملی و دربند.",
        stops: [
          { city: "تهران", placeName: "برج آزادی" },
          { city: "تهران", placeName: "موزه ملی ایران" },
          { city: "تهران", placeName: "دربند" },
        ],
      },
    ],
  },
  {
    id: "qeshm-geo",
    name: "قشم و ژئوپارک",
    province: "هرمزگان",
    city: "قشم",
    days: 3,
    summary: "جزیره، دره ستارگان و ساحل جنوبی.",
    image: "/suggestions/qeshm.jpg",
    highlights: ["ژئوپارک", "دره ستارگان", "هنگام"],
    itinerary: [
      {
        day: 1,
        title: "ژئوپارک",
        body: "ژئوپارک جهانی قشم.",
        stops: [{ city: "قشم", placeName: "ژئوپارک قشم" }],
      },
      {
        day: 2,
        title: "دره ستارگان",
        body: "دره ستارگان.",
        stops: [{ city: "قشم", placeName: "دره ستارگان" }],
      },
      {
        day: 3,
        title: "چاهکوه",
        body: "دره چاهکوه.",
        stops: [{ city: "قشم", placeName: "دره چاهکوه" }],
      },
    ],
  },
  {
    id: "bandar-abbas",
    name: "بندرعباس کوتاه",
    province: "هرمزگان",
    city: "بندرعباس",
    days: 2,
    summary: "ساحل خلیج فارس و نشانه‌های شهری بندر.",
    image: "/suggestions/bandarabbas.jpg",
    highlights: ["معبد هندوها", "ساحل", "بازار"],
    itinerary: [
      {
        day: 1,
        title: "شهر",
        body: "معبد هندوها و حمام گله‌داری.",
        stops: [
          { city: "بندرعباس", placeName: "معبد هندوها" },
          { city: "بندرعباس", placeName: "حمام گله‌داری" },
        ],
      },
      {
        day: 2,
        title: "ساحل",
        body: "ساحل سورو.",
        stops: [{ city: "بندرعباس", placeName: "ساحل سورو" }],
      },
    ],
  },
  {
    id: "tabriz-elgoli",
    name: "تبریز و ائل‌گلی",
    province: "آذربایجان شرقی",
    city: "تبریز",
    days: 2,
    summary: "بازار جهانی، محله‌های تاریخی و باغ ائل‌گلی.",
    image: "/suggestions/tabriz.jpg",
    highlights: ["ائل‌گلی", "بازار تبریز", "مسجد کبود"],
    itinerary: [
      {
        day: 1,
        title: "مرکز تاریخی",
        body: "بازار سرپوشیده و مسجد کبود.",
        stops: [
          { city: "تبریز", placeName: "بازار تبریز" },
          { city: "تبریز", placeName: "مسجد کبود" },
        ],
      },
      {
        day: 2,
        title: "ائل‌گلی",
        body: "باغ و استخر ائل‌گلی.",
        stops: [{ city: "تبریز", placeName: "ائل‌گلی" }],
      },
    ],
  },
  {
    id: "ramsar-mazandaran",
    name: "رامسر و غرب مازندران",
    province: "مازندران",
    city: "رامسر",
    days: 2,
    summary: "کاخ، جنگل و ساحل در یک ایستگاه کوتاه.",
    image: "/suggestions/ramsar.jpg",
    highlights: ["کاخ رامسر", "جواهرده", "ساحل"],
    itinerary: [
      {
        day: 1,
        title: "شهر رامسر",
        body: "کاخ مرمر رامسر.",
        stops: [{ city: "رامسر", placeName: "کاخ مرمر رامسر" }],
      },
      {
        day: 2,
        title: "جنگل و تله‌کابین",
        body: "تله‌کابین و جنگل دالخانی.",
        stops: [
          { city: "رامسر", placeName: "تله‌کابین رامسر" },
          { city: "رامسر", placeName: "جنگل دالخانی" },
        ],
      },
    ],
  },
  {
    id: "shiraz-literary",
    name: "شیراز ادبی",
    province: "فارس",
    city: "شیراز",
    days: 2,
    summary: "حافظ و سعدی؛ دو روز آرام در باغ و آرامگاه.",
    image: "/suggestions/hafez.jpg",
    highlights: ["حافظیه", "سعدیه", "باغ دلگشا"],
    itinerary: [
      {
        day: 1,
        title: "حافظیه",
        body: "آرامگاه حافظ و گشت عصرگاهی باغ.",
        stops: [{ city: "شیراز", placeName: "حافظیه" }],
      },
      {
        day: 2,
        title: "سعدیه",
        body: "سعدیه و باغ دلگشا.",
        stops: [
          { city: "شیراز", placeName: "سعدیه" },
          { city: "شیراز", placeName: "باغ دلگشا" },
        ],
      },
    ],
  },
];

export function getTour(id: string): Tour | undefined {
  return TOURS.find((tour) => tour.id === id);
}

export function listProvinces(): string[] {
  return [...new Set(TOURS.map((tour) => tour.province))];
}

export function groupToursByProvince(tours: Tour[] = TOURS): { province: string; tours: Tour[] }[] {
  const map = new Map<string, Tour[]>();
  for (const tour of tours) {
    const list = map.get(tour.province) ?? [];
    list.push(tour);
    map.set(tour.province, list);
  }
  return [...map.entries()].map(([province, group]) => ({ province, tours: group }));
}

export function groupToursByProvinceThenCity(
  tours: Tour[] = TOURS,
): { province: string; cities: { city: string; plans: Tour[] }[] }[] {
  const provinces = groupToursByProvince(tours);
  return provinces.map(({ province, tours: provinceTours }) => {
    const cities = new Map<string, Tour[]>();
    for (const plan of provinceTours) {
      const list = cities.get(plan.city) ?? [];
      list.push(plan);
      cities.set(plan.city, list);
    }
    return {
      province,
      cities: [...cities.entries()].map(([city, plans]) => ({ city, plans })),
    };
  });
}
