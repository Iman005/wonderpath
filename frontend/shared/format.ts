// Iranian-formatted numbers/currency. Centralized here per the
// architecture spec's Localization Module responsibility, even though
// in the frontend folder layout it lives under shared/ rather than i18n/
// (i18n/ holds strings; this holds locale-aware formatting).

import { isoToJalali, JALALI_MONTHS } from "@/shared/jalali";

const faDigits = ["۰", "۱", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹"];

export function toPersianDigits(input: string | number): string {
  return String(input).replace(/[0-9]/g, (d) => faDigits[Number(d)]);
}

export function formatToman(amount: number | null | undefined): string {
  if (amount === null || amount === undefined) {
    return "نامشخص";
  }
  const formatted = new Intl.NumberFormat("en-US").format(Math.round(amount));
  return `${toPersianDigits(formatted)} تومان`;
}

export function formatDistanceKm(km: number | null | undefined, isDriving = true): string | null {
  if (km === null || km === undefined) return null;
  const rounded = km >= 100 ? Math.round(km) : Math.round(km * 10) / 10;
  const formatted = new Intl.NumberFormat("en-US", {
    maximumFractionDigits: km >= 100 ? 0 : 1,
  }).format(rounded);
  const label = `${toPersianDigits(formatted)} کیلومتر`;
  return isDriving ? label : `${label} (تقریبی)`;
}

export function formatOriginDistanceLine(
  km: number | null | undefined,
  minutes: number | null | undefined,
  isDriving = true
): string | null {
  const distance = formatDistanceKm(km, isDriving);
  if (!distance) return null;
  if (isDriving) {
    const duration = formatDrivingDuration(minutes);
    return duration ? `${distance} · ${duration}` : distance;
  }
  return distance;
}

export function formatDrivingDuration(minutes: number | null | undefined): string | null {
  const short = formatDrivingDurationShort(minutes);
  if (!short) return null;
  return `${short} رانندگی`;
}

/** Duration without the trailing «رانندگی» — for labeled metric cells. */
export function formatDrivingDurationShort(minutes: number | null | undefined): string | null {
  if (minutes === null || minutes === undefined) return null;
  const rounded = Math.max(1, Math.round(minutes));
  const hours = Math.floor(rounded / 60);
  const mins = rounded % 60;
  if (hours <= 0) {
    return `~${toPersianDigits(String(mins))} دقیقه`;
  }
  if (mins === 0) {
    return `~${toPersianDigits(String(hours))} ساعت`;
  }
  return `~${toPersianDigits(String(hours))} ساعت و ${toPersianDigits(String(mins))} دقیقه`;
}

const persianDigitMap: Record<string, string> = {
  "۰": "0",
  "۱": "1",
  "۲": "2",
  "۳": "3",
  "۴": "4",
  "۵": "5",
  "۶": "6",
  "۷": "7",
  "۸": "8",
  "۹": "9",
  "٠": "0",
  "١": "1",
  "٢": "2",
  "٣": "3",
  "٤": "4",
  "٥": "5",
  "٦": "6",
  "٧": "7",
  "٨": "8",
  "٩": "9",
};

export function parseTomanInput(raw: string): number | null {
  const normalized = raw
    .replace(/[۰-۹٠-٩]/g, (digit) => persianDigitMap[digit] ?? digit)
    .replace(/تومان/g, "")
    .replace(/[,\s_٬،]/g, "")
    .trim();
  if (!normalized) return null;
  const value = Number(normalized);
  if (!Number.isFinite(value) || value < 0) return null;
  return value;
}

export function formatGroupedTomanInput(raw: string): string {
  const normalized = raw
    .replace(/[۰-۹٠-٩]/g, (digit) => persianDigitMap[digit] ?? digit)
    .replace(/[^\d]/g, "");
  if (!normalized) return "";
  const digits = normalized.replace(/^0+(?=\d)/, "");
  const grouped = digits.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return toPersianDigits(grouped);
}

export function groupedTomanFromAmount(amount: number | null | undefined): string {
  if (amount == null || !Number.isFinite(amount)) return "";
  return formatGroupedTomanInput(String(Math.round(amount)));
}

export function formatDayLabel(dayNumber: number): string {
  return `روز ${toPersianDigits(dayNumber)}`;
}

const DAY_ORDINALS = [
  "",
  "اول",
  "دوم",
  "سوم",
  "چهارم",
  "پنجم",
  "ششم",
  "هفتم",
  "هشتم",
  "نهم",
  "دهم",
  "یازدهم",
  "دوازدهم",
];

export function formatDayOrdinal(dayNumber: number): string {
  if (dayNumber >= 1 && dayNumber < DAY_ORDINALS.length) {
    return `روز ${DAY_ORDINALS[dayNumber]}`;
  }
  return formatDayLabel(dayNumber);
}

export function formatCoordinates(lat: number, lng: number): string {
  const latText = toPersianDigits(lat.toFixed(4));
  const lngText = toPersianDigits(lng.toFixed(4));
  return `${latText}، ${lngText}`;
}

export function placeImageUrls(place: {
  image: string | null;
  extra_images?: string[] | null;
}): string[] {
  const urls = [place.image, ...(place.extra_images ?? [])].filter((url): url is string => Boolean(url));
  return [...new Set(urls)];
}

export function formatIsoDate(iso: string | null | undefined): string {
  if (!iso) return "";
  try {
    const [jy, jm, jd] = isoToJalali(iso);
    return `${toPersianDigits(jd)} ${JALALI_MONTHS[jm - 1]} ${toPersianDigits(jy)}`;
  } catch {
    return toPersianDigits(iso.slice(0, 10));
  }
}

export function formatJalaliSlash(iso: string | null | undefined): string {
  if (!iso) return "";
  try {
    const [jy, jm, jd] = isoToJalali(iso);
    return toPersianDigits(`${jy}/${jm}/${jd}`);
  } catch {
    return toPersianDigits(iso.slice(0, 10));
  }
}

export function inclusiveDayCount(startIso: string, endIso: string): number {
  const start = Date.parse(`${startIso.slice(0, 10)}T00:00:00`);
  const end = Date.parse(`${endIso.slice(0, 10)}T00:00:00`);
  if (!Number.isFinite(start) || !Number.isFinite(end)) return 0;
  return Math.round((end - start) / 86_400_000) + 1;
}

export function addDaysToIso(iso: string, days: number): string {
  const date = new Date(`${iso.slice(0, 10)}T00:00:00`);
  date.setDate(date.getDate() + days);
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${date.getFullYear()}-${month}-${day}`;
}

export function dayDateIso(tripStart: string | null | undefined, dayNumber: number, dayDate?: string | null): string | null {
  if (dayDate) return dayDate.slice(0, 10);
  if (!tripStart) return null;
  return addDaysToIso(tripStart, dayNumber - 1);
}
