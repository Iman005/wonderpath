import fa from "@/i18n/fa";
import type { PlaceKind } from "@/shared/types";

export function feeLabelForKind(kind?: string | null): string {
  if (kind === "lodging") return fa.destination.nightlyRate;
  if (kind === "dining") return fa.destination.mealCost;
  return fa.destination.entranceFee;
}

export function isLodging(kind?: string | null): boolean {
  return kind === "lodging";
}

export function asPlaceKind(kind?: string | null): PlaceKind {
  if (kind === "lodging" || kind === "dining") return kind;
  return "attraction";
}
